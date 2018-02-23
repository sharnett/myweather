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

_DEFAULT_NUM_HOURS = 12
_DEFAULT_UNITS = 'F'
_DEFAULT_USER_INPUT = '10027'
_DEFAULT_LOCATION_URL = '/q/zmw:10027.1.99999'
_DEFAULT_LOCATION_NAME = '10027 -- New York, NY'
_DEFAULT_LOCATION = Location(_DEFAULT_LOCATION_URL, _DEFAULT_LOCATION_NAME)

app = flask.Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY', 'development')
API_KEY = os.environ.get('WUNDERGROUND_KEY', 'development')
DEBUG = True if SECRET_KEY == 'development' else False
if not DEBUG:
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


def get_location(user_input, opener=urlopen):
    ''' Get the Location corresponding the user input

    Locations are keyed by url and cache their weather data, which we want
    to use if we can.

    First, we look for the user_input in the Lookup table. If there was a
    previous lookup, return the corresponding location.

    If not, use the autocomplete API to get the url. If that url exists in the
    Location table, return that location.

    Otherwise, create and return a new Location built from the results of the
    autocomplete API.

    If the autocomplete API fails, return a default location.
    '''
    last_lookup = (Lookup.query.filter_by(user_input=user_input)
                   .order_by(Lookup.date.desc()).first())
    log.info('db result for most recent lookup of this location: ' + str(last_lookup))
    if (last_lookup is not None and
            (datetime.now()-last_lookup.date).seconds < 604800):  # 7 days
        log.info('got location info from the cache of a previous lookup')
        return last_lookup.location, user_input
    try:
        url, name = autocomplete_user_input(user_input, opener=opener)
        log.info('got location info from autocomplete API')
        log.info('%s -> %s, %s', user_input, url, name)
        location = Location.query.get(url)
        if location is None:
            log.info('no info for that location, creating a new entry')
            location = Location(url, name)
        else:
            log.info('already have info for that location, reusing it')
        return location, user_input
    except IndexError, KeyError:
        flask.flash('seanweather didnt like that, please try another city or '
                    'zipcode')
        log.warning('failed to parse: %s. Using %s', user_input,
                    _DEFAULT_USER_INPUT)
        # Check for a default in the db so we can make use of any existing cache
        location = Location.query.get(_DEFAULT_LOCATION_URL)
        if location is None:
            location = _DEFAULT_LOCATION
        return location, _DEFAULT_USER_INPUT


def parse_temps(weather_data, num_hours=24, units=_DEFAULT_UNITS):
    ''' Get current temp, and min/max temps over the next num_hours '''
    temps = []
    key = 'temp_c' if units == 'C' else 'temp'
    for d in weather_data[:num_hours]:
        temps.append(int(d[key]))
    if not temps:
        return '', '', ''
    return temps[0], max(temps), min(temps)


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
        self.units = _DEFAULT_UNITS
        self.previous = None

    def update(self):
        log.info('STARTING')
        self.previous = \
            session.get('sw', dict(units=_DEFAULT_UNITS,
                                   user_input=_DEFAULT_USER_INPUT,
                                   num_hours=_DEFAULT_NUM_HOURS))
        self.update_units()
        self.update_location()
        self.update_num_hours()
        self.update_weather_data()
        self.update_current_condtions()
        session['sw'] = dict(units=self.units, user_input=self.user_input,
                             num_hours=self.num_hours)
        log.info('FINISHED with %s' % self.user_input)

    def update_units(self):
        self.units = self.previous['units']
        new_units = request.args.get('new_units')
        if new_units in ('C', 'F') and new_units != self.units:
            self.units = new_units
        log.warning('units: %s', self.units)

    def update_location(self):
        user_input = request.args.get('user_input',
                                      self.previous['user_input'])
        self.location, self.user_input = get_location(user_input)
        log.info('%s', self.location)

    def update_num_hours(self):
        try:
            self.num_hours = int(request.args.get('num_hours',
                                                  self.previous['num_hours']))
        except:
            flask.flash('seanweather didnt like the number of hours, using %s',
                        _DEFAULT_NUM_HOURS)
            log.error('bad number of hours')
            self.num_hours = _DEFAULT_NUM_HOURS

    def _was_recently_updated(self, max_seconds=2700):
        return ((datetime.now() - self.location.last_updated).seconds <=
                max_seconds)

    def update_weather_data(self):
        if self.location.cache and self._was_recently_updated():
            log.info('weather for %s was recently cached, reusing',
                     self.location.name)
        else:
            num_secs = (datetime.now() - self.location.last_updated).seconds
            log.info('%d chars in cache, %ds since last update'
                     % (len(self.location.cache), num_secs))
            log.info('using weather API for %s', self.location.name)
            wd = weather_for_url(self.location.url, API_KEY)
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

    def update_current_condtions(self):
        self.current_temp, self.max_temp, self.min_temp = parse_temps(
            self.weather_data, units=self.units)
        self.icon = (self.weather_data[0].get('icon')
                     if self.weather_data else '')


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
