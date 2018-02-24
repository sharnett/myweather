import flask
import json
import logging
import logging.handlers
import os
from flask import render_template, request, session
from wunderground import weather_for_url, autocomplete_user_input
from os.path import dirname, abspath, isfile
from database import db, Location, Lookup
from datetime import datetime
from urllib2 import urlopen
from collections import namedtuple
from enum import Enum

class Units(Enum):
    F = 1
    C = 2

    @classmethod
    def get(cls, name, default=None):
        try:
            return cls[name]
        except KeyError:
            return default

_DEFAULT_NUM_HOURS = 12
_DEFAULT_USER_INPUT = '10027'
_DEFAULT_LOCATION_URL = '/q/zmw:10027.1.99999'
_DEFAULT_LOCATION_NAME = '10027 -- New York, NY'
_DEFAULT_LOCATION = Location(_DEFAULT_LOCATION_URL, _DEFAULT_LOCATION_NAME)
CookieData = namedtuple('CookieData', ['units', 'user_input', 'num_hours'])
_DEFAULT_COOKIE = CookieData(Units.F, _DEFAULT_USER_INPUT, _DEFAULT_NUM_HOURS)

app = flask.Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY', 'development')
API_KEY = os.environ.get('WUNDERGROUND_KEY', 'development')
DEBUG = True if SECRET_KEY == 'development' else False
if DEBUG:
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)
else:
    import logging
    from TlsSMTPHandler import TlsSMTPHandler
    from email_credentials import email_credentials
    mail_handler = TlsSMTPHandler(*email_credentials())
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.db'
app.config.from_object(__name__)
db.init_app(app)

log = logging.getLogger('seanweather')
log.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler('seanweather.log', maxBytes=10000000)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

if not isfile(dirname(abspath(__file__)) + '/db.db'):
    log.warning('db doesnt exist, creating a new one')
    with app.app_context():
        db.create_all()


def main():
    app.run(host='0.0.0.0')


class SeanWeather(object):
    def __init__(self):
        self.data_string = ''
        self.location = None
        self.user_input = _DEFAULT_USER_INPUT
        self.num_hours = _DEFAULT_NUM_HOURS
        self.current_temp = ''
        self.max_temp = ''
        self.min_temp = ''
        self.icon = ''
        self.units = None
        self.previous = None
        self.weather_data = ''

    def update(self):
        log.info('STARTING')
        self.previous = CookieData(*session.get('sw2', _DEFAULT_COOKIE))
        self.update_units()
        self.update_location()
        self.update_num_hours()
        self.update_weather_data()
        self.update_current_conditions()
        session['sw2'] = CookieData(units=self.units.name, user_input=self.user_input,
                                    num_hours=self.num_hours)
        log.info('FINISHED with %s' % self.user_input)

    def update_units(self):
        self.units = Units[self.previous.units]
        request_units = request.args.get('new_units')
        log.info('self.units: %s, request units: %s', self.units, request_units)
        self.units = Units.get(request_units, self.units)
        log.info('new units: %s', self.units)

    def update_location(self, opener=urlopen):
        ''' Get the Location corresponding to the user input

        Locations are keyed by url and cache their weather data, which we want to
        use if we can.

        First, we look for the user_input in the Lookup table. If there was a
        previous lookup within the last seven days, we return the corresponding
        location.

        If the user input is not in the Lookup table, we use the autocomplete API
        to get a url and name for the user input. If the API fails, we use the
        default url and name, and replace the user_input with the default so we
        don't cache it.

        If the url exists in the Location table, we return that location. Otherwise,
        we create and return a new Location from the url and name.
        '''
        user_input = request.args.get('user_input',
                                      self.previous.user_input)
        last_lookup = (Lookup.query.filter_by(user_input=user_input)
                       .order_by(Lookup.date.desc()).first())
        log.info('db result for most recent lookup of this location: %s', last_lookup)
        if (last_lookup is not None and
                (datetime.now()-last_lookup.date).seconds < 604800):  # 7 days
            log.info('got location info from the cache of a previous lookup')
            self.location = last_lookup.location
            return
        # No recent lookups for this user input, so check the autocomplete API
        try:
            url, name = autocomplete_user_input(user_input, opener=opener)
            log.info('got location info from autocomplete API:%s -> %s, %s',
                     user_input, url, name)
        # That didn't work, so just use the default url and name
        except IndexError, KeyError:
            flask.flash('I didnt like that, please try another city or zipcode')
            log.warning('%s failed. Using %s', user_input, _DEFAULT_USER_INPUT)
            url, name = _DEFAULT_LOCATION_URL, _DEFAULT_LOCATION_NAME
            self.user_input = _DEFAULT_USER_INPUT
        # Now look for the url in the Location table
        self.location = Location.query.get(url)
        if self.location is None:
            log.info('no info for that location, creating a new entry')
            self.location = Location(url, name)
        else:
            log.info('already have info for that location, reusing it')
        log.info('%s', self.location)

    def update_num_hours(self):
        try:
            self.num_hours = int(request.args.get('num_hours',
                                                  self.previous.num_hours))
        except ValueError:
            flask.flash('seanweather didnt like the number of hours, using %d' %
                        _DEFAULT_NUM_HOURS)
            log.error('bad number of hours. request: %s, prev: %s',
                      request.args.get('num_hours'), self.previous.num_hours)
            self.num_hours = _DEFAULT_NUM_HOURS

    def update_weather_data(self, weather_getter=weather_for_url):
        if self.location.cache and self._was_recently_updated():
            log.info('weather for %s was recently cached, reusing',
                     self.location.name)
        else:
            num_secs = (datetime.now() - self.location.last_updated).seconds
            log.info('%d chars in cache, %ds since last update'
                     % (len(self.location.cache), num_secs))
            log.info('using weather API for %s', self.location.name)
            wd = weather_getter(self.location.url, API_KEY)
            self.location.cache = json.dumps(wd)
            if wd:
                self.location.last_updated = datetime.now()
            else:
                log.warning("didn't get any results from weather API")
        self.location = db.session.merge(self.location)
        db.session.add(Lookup(self.user_input, self.location))
        db.session.commit()
        self.weather_data = json.loads(self.location.cache)
        self.data_string = jsonify(self.weather_data[:self.num_hours])

    def update_current_conditions(self):
        ''' Update current temp and icon, and min/max temps over the next 24 hours '''
        if not self.weather_data:
            self.current_temp, self.max_temp, self.min_temp, self.icon = '', '', '', ''
            return
        temp_key = 'temp_c' if self.units == Units.C else 'temp'
        temps = [int(weather_day[temp_key]) for weather_day in self.weather_data[:24]]
        self.current_temp, self.max_temp, self.min_temp, self.icon = (
            temps[0], max(temps), min(temps), self.weather_data[0].get('icon'))

    def _was_recently_updated(self, max_seconds=2700):
        return ((datetime.now() - self.location.last_updated).seconds <=
                max_seconds)


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/', methods=['GET'])
def home():
    sw = SeanWeather()
    sw.update()
    return render_template('weather_form.html', sw=sw)


@app.route('/fake')
def fake():
    log.info('STARTING -- fake')
    sw = SeanWeather()
    sw.weather_data = [
            {'temp': u'85', 'feel': u'83', 'pop': u'0', 'icon_pos': 100,
                'feel_c': u'28', 'temp_c': u'29', 'date': 1498334400000,
                'icon': u'http://icons.wxug.com/i/c/k/partlycloudy.gif'},
            {'temp': u'85', 'feel': u'83', 'pop': u'0', 'icon_pos': 100,
                'feel_c': u'28', 'temp_c': u'29', 'date': 1498338000000,
                'icon': u'http://icons.wxug.com/i/c/k/partlycloudy.gif'},
            {'temp': u'85', 'feel': u'83', 'pop': u'0', 'icon_pos': 100,
                'feel_c': u'28', 'temp_c': u'29', 'date': 1498341600000,
                'icon': u'http://icons.wxug.com/i/c/k/partlycloudy.gif'},
            {'temp': u'85', 'feel': u'83', 'pop': u'0', 'icon_pos': 100,
                'feel_c': u'28', 'temp_c': u'29', 'date': 1498345200000,
                'icon': u'http://icons.wxug.com/i/c/k/clear.gif'},
            {'temp': u'83', 'feel': u'82', 'pop': u'0', 'icon_pos': 100,
                'feel_c': u'28', 'temp_c': u'28', 'date': 1498348800000,
                'icon': u'http://icons.wxug.com/i/c/k/clear.gif'},
            {'temp': u'81', 'feel': u'81', 'pop': u'0', 'icon_pos': 100,
                'feel_c': u'27', 'temp_c': u'27', 'date': 1498352400000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'79', 'feel': u'79', 'pop': u'1', 'icon_pos': 100,
                'feel_c': u'26', 'temp_c': u'26', 'date': 1498356000000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'78', 'feel': u'78', 'pop': u'2', 'icon_pos': 100,
                'feel_c': u'26', 'temp_c': u'26', 'date': 1498359600000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'77', 'feel': u'77', 'pop': u'2', 'icon_pos': 100,
                'feel_c': u'25', 'temp_c': u'25', 'date': 1498363200000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'75', 'feel': u'75', 'pop': u'2', 'icon_pos': 100,
                'feel_c': u'24', 'temp_c': u'24', 'date': 1498366800000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'74', 'feel': u'74', 'pop': u'3', 'icon_pos': 100,
                'feel_c': u'23', 'temp_c': u'23', 'date': 1498370400000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'73', 'feel': u'73', 'pop': u'3', 'icon_pos': 100,
                'feel_c': u'23', 'temp_c': u'23', 'date': 1498374000000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'}]
    sw.data_string = jsonify(sw.weather_data)
    sw.icon = 'http://icons.wxug.com/i/c/k/nt_clear.gif'
    sw.location = Location('', name='10027 -- New York, NY')
    sw.user_input = 'chilled'
    sw.num_hours = 12
    sw.current_temp, sw.max_temp, sw.min_temp = 75, 80, 65
    log.info('FINISHED with %s -- fake', sw.user_input)
    return render_template('weather_form.html', sw=sw)


@app.route('/discuss')
def discuss():
    return render_template('discuss.html')


def jsonify(weather_data):
    row_string = ("{{date: new Date({date}), icon: '{icon}', "
                  "icon_pos: {icon_pos}, temp: {temp}, pop: {pop}, "
                  "feel: {feel}, temp_c: {temp_c}, feel_c: {feel_c}}}")
    stringified = [row_string.format(**row) for row in weather_data]
    return "[" + ",\n".join(stringified) + "]"


if __name__ == '__main__':
    main()
