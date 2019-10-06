from __future__ import print_function

from collections import namedtuple
import json
import logging
import re
import time
import urllib
from os import environ
from future.moves.urllib.request import urlopen
from future.moves.urllib.error import URLError

from config import log

Location = namedtuple('Location', ['location_id', 'name', 'country'])

# https://openweathermap.org/weather-conditions and
# https://www.wunderground.com/weather/api/d/docs?d=resources/icon-sets#icon_set__11
_ICON_MAP = {'01d': 'clear', '02d': 'partlycloudy', '03d': 'cloudy',
        '04d': 'cloudy', '09d': 'rain', '10d': 'rain', '11d': 'tstorms',
        '13d': 'snow', '50d': 'fog',
        '01n': 'nt_clear', '02n': 'nt_partlycloudy', '03n': 'cloudy',
        '04n': 'cloudy', '09n': 'rain', '10n': 'rain', '11n': 'tstorms',
        '13n': 'snow', '50n': 'fog'}

# Hack: this controls the y-position of the icons
_MAX_POP = 10


def weather_for_user_input(user_input, api_key):
    return _parse_json(_json_for_user_input(user_input, api_key))


def _json_for_user_input(user_input, api_key, opener=urlopen):
    if api_key == 'development':
        log.error('You need to set OPENWEATHERMAP_KEY in your environment')
        return {}
    base_url = (
        'http://api.openweathermap.org/data/2.5/forecast?{param}={user_input}&APPID={key}')
    param = 'zip' if re.match(r'\d\d\d\d\d', user_input) else 'q'
    url = base_url.format(param=param, key=api_key, user_input=urllib.quote(user_input))
    log.info(url)
    for i in range(3):
        try:
            response = json.load(opener(url))
            log.info(str(response)[:100])
            return response
        except URLError:
            time.sleep(i)
    raise URLError('urlopen timeout max retries for %s=%s' % (param, user_input))


def _parse_json(json_data):
    ''' Parse json returned from OpenWeatherMap API into list of dicts with
        only the data we care about.
    '''

    if ('list' not in json_data
            or not json_data['list']
            or 'city' not in json_data):
        log.error('json data is ill-formed')
        return [], Location(0, '', '')

    def get_dict(row):
        k = row['main']['temp']
        f = k*9/5 - 459.67
        c = k - 273.15
        rh = row['main']['humidity']
        rain = row['rain'].get('3h', 0.) if 'rain' in row else 0.
        snow = row['snow'].get('3h', 0.) if 'snow' in row else 0.
        precipitation = rain + snow
        wind_mps = row['wind'].get('speed', 0.) if 'wind' in row else 0.
        wind_mph = 2.23694 * wind_mps

        if f <= 50 and wind_mph >= 3: # wind chill
            feel = (35.74
                    + 0.6215 * f
                    - 35.75 * wind_mph**0.16
                    + 0.4275 * f * wind_mph**0.16)
        elif f >= 80 and rh >= 40: # heat index
            feel = (-42.379
                    + 2.04901523 * f
                    + 10.14333127 * rh
                    - 0.22475541 * f * rh
                    - 6.83783e-3 * f**2
                    - 5.481717e-2 * rh**2
                    + 1.22874e-3 * f**2 * rh
                    + 8.5282e-4 * f * rh**2
                    - 1.99e-6 * f**2 * rh**2)
        else:
            feel = f
        feel_c = (feel - 32) * 5 / 9
        icon_type = _ICON_MAP[row['weather'][0]['icon']]
        icon = '/static/icons/%s.gif' % icon_type

        return dict(
            date=row['dt']*1000,
            icon=icon,
            icon_pos=_MAX_POP,
            temp=str(int(round(f))), # temperature in Fahrenheit
            # mm rain over three hour window
            pop='%.1f' % precipitation,
            feel=str(int(round(feel))), # wind chill / heat index
            temp_c=str(int(round(c))),
            feel_c=str(int(round(feel_c))))

    weather_data =  [get_dict(row) for row in json_data['list']]

    city = json_data['city']
    city_id = city.get('id', hash((city['coord']['lat'], city['coord']['lon'])))
    location = Location(city_id, city['name'], city['country'])

    return weather_data, location


if __name__ == "__main__":
    location = 'london'
    try:
        api_key = environ['WUNDERGROUND_KEY']
    except KeyError:
        print('enter weather underground api key:')
        api_key = raw_input()
    json_data = _json_for_location(location, api_key)
    weather_data = _parse_json(json_data)[:12]
    for row in weather_data:
        print(row)
