import json
from collections import namedtuple
from datetime import datetime
from enum import Enum
from flask import flash, render_template, request, session
from future.moves.urllib.request import urlopen

from app import app, db
from config import log, API_KEY
from app.database import Lookup
from app.wunderground import weather_for_user_input, Location, WundergroundError

class Units(Enum):
    F = 1
    C = 2
    @classmethod
    def get(cls, name, default=None):
        try:
            return cls[name]
        except KeyError:
            return default

CookieData = namedtuple('CookieData', ['units', 'user_input', 'num_hours'])

_NUM_POINTS_IN_DAY = 8
_DEFAULT_NUM_HOURS = 24
_DEFAULT_USER_INPUT = 'New York'
_DEFAULT_LOCATION = Location(5128581, 'New York', 'US')
_DEFAULT_UNITS = Units.F
_DEFAULT_COOKIE = CookieData(Units.F, _DEFAULT_USER_INPUT, _DEFAULT_NUM_HOURS)


class SeanWeather(object):
    def __init__(self):
        self.data_string = ''
        self.location = _DEFAULT_LOCATION
        self.user_input = _DEFAULT_USER_INPUT
        self.num_hours = _DEFAULT_NUM_HOURS
        self.current_temp = ''
        self.max_temp = ''
        self.min_temp = ''
        self.icon = ''
        self.units = _DEFAULT_UNITS
        self.previous = _DEFAULT_COOKIE
        self.weather_data = ''

    def update(self):
        log.info('STARTING')
        self.previous = CookieData(*session.get('sw2', _DEFAULT_COOKIE))
        self.update_units()
        self.update_num_hours()
        self.update_weather_data()
        self.update_current_conditions()
        session['sw2'] = CookieData(units=self.units.name, user_input=self.user_input,
                                    num_hours=self.num_hours)
        log.info('FINISHED with %s' % self.user_input)

    def update_units(self):
        self.units = Units.get(self.previous.units, Units.F)
        request_units = request.args.get('new_units')
        log.info('self.units: %s, request units: %s', self.units, request_units)
        self.units = Units.get(request_units, self.units)
        log.info('new units: %s', self.units)

    def update_num_hours(self):
        try:
            self.num_hours = int(request.args.get('num_hours',
                                                  self.previous.num_hours))
        except ValueError:
            flash('seanweather didnt like the number of hours, using %d' %
                        _DEFAULT_NUM_HOURS)
            log.error('bad number of hours. request: %s, prev: %s',
                      request.args.get('num_hours'), self.previous.num_hours)
            self.num_hours = _DEFAULT_NUM_HOURS
        log.info('num hours: %s', self.num_hours)

    def update_weather_data(self, weather_getter=weather_for_user_input):
        self.user_input = request.args.get('user_input',
                                           self.previous.user_input)
        log.info('using weather API for %s', self.user_input)
        try:
            self.weather_data, self.location = weather_getter(self.user_input, API_KEY)
        except WundergroundError:
            flash('seanweather didnt like the location, please try something else')
            log.error("failed weather API call")
            return
        db.session.add(Lookup(self.user_input, self.location))
        db.session.commit()
        self.data_string = jsonify(self.weather_data[:int(self.num_hours / 3)])

    def update_current_conditions(self):
        ''' Update current temp and icon, and min/max temps over the next 24 hours '''
        if not self.weather_data:
            self.current_temp, self.max_temp, self.min_temp, self.icon = '', '', '', ''
            return
        temp_key = 'temp_c' if self.units == Units.C else 'temp'
        temps = [int(round(float(weather_day[temp_key]))) for weather_day in self.weather_data[:_NUM_POINTS_IN_DAY]]
        self.current_temp, self.max_temp, self.min_temp, self.icon = (
            temps[0], max(temps), min(temps), self.weather_data[0].get('icon'))


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
            {'temp': u'85', 'feel': u'83', 'pop': u'0', 'icon_pos': 10,
                'feel_c': u'28', 'temp_c': u'29', 'date': 1498334400000,
                'icon': u'http://icons.wxug.com/i/c/k/partlycloudy.gif'},
            {'temp': u'85', 'feel': u'83', 'pop': u'0', 'icon_pos': 10,
                'feel_c': u'28', 'temp_c': u'29', 'date': 1498345200000,
                'icon': u'http://icons.wxug.com/i/c/k/clear.gif'},
            {'temp': u'79', 'feel': u'79', 'pop': u'1', 'icon_pos': 10,
                'feel_c': u'26', 'temp_c': u'26', 'date': 1498356000000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'78', 'feel': u'78', 'pop': u'2', 'icon_pos': 10,
                'feel_c': u'26', 'temp_c': u'26', 'date': 1498366800000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'77', 'feel': u'77', 'pop': u'2', 'icon_pos': 10,
                'feel_c': u'25', 'temp_c': u'25', 'date': 1498377600000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'75', 'feel': u'75', 'pop': u'2', 'icon_pos': 10,
                'feel_c': u'24', 'temp_c': u'24', 'date': 1498388400000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'74', 'feel': u'74', 'pop': u'3', 'icon_pos': 10,
                'feel_c': u'23', 'temp_c': u'23', 'date': 1498399200000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'},
            {'temp': u'73', 'feel': u'73', 'pop': u'3', 'icon_pos': 10,
                'feel_c': u'23', 'temp_c': u'23', 'date': 1498410000000,
                'icon': u'http://icons.wxug.com/i/c/k/nt_clear.gif'}]
    sw.data_string = jsonify(sw.weather_data)
    sw.icon = 'http://icons.wxug.com/i/c/k/nt_clear.gif'
    sw.user_input = 'chilled'
    sw.update_current_conditions()
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
