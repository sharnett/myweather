import json
import logging
import urllib
from urllib2 import urlopen, URLError
from os import environ
from time import sleep

logging.basicConfig()
log = logging.getLogger(__name__)

_KEY = environ['WUNDERGROUND_KEY']
_BASE_URL = 'http://api.wunderground.com/api/{key}/hourly10day{location_url}.json'

def _parse_json(json_data):
    w = json_data
    if not 'hourly_forecast' in w or not w['hourly_forecast']:
        return ''
    def get_row(f):
        return dict(
            date=int(f['FCTTIME']['epoch'])*1000,
            icon=f['icon_url'],
            icon_pos=100,
            pop=f['pop'],                   # probability of precipitation
            temp=f['temp']['english'],      # temperature in Fahrenheit
            temp_c=f['temp']['metric'],     # Celsius
            feel=f['feelslike']['english'], # temperature it feels like, in Fahrenheit
            feel_c=f['feelslike']['metric'])
    return [get_row(f) for f in w['hourly_forecast']]

def parse_user_input(s):
    ''' Takes contents of 'enter zip code or city' field and gives it to the wunderground autocomplete API.
    Returns the URL path and name of the top result, e.g.

    '/q/zmw:10027.1.99999', '10027 - New York, NY', '10027.1.99999'
    '''
    url = 'http://autocomplete.wunderground.com/aq?query=%s' % urllib.quote(s.encode('utf-8'))
    response = json.load(urlopen(url))
    top_result = response['RESULTS'][0] # will raise an IndexError if RESULTS is empty
    url, location_name, zmw = top_result['l'], top_result['name'], top_result['zmw']
    logging.info(url)
    return url, location_name, zmw
  
def _json_for_url(location_url):
    url = _BASE_URL.format(key=_KEY, location_url=location_url)
    for i in range(3):
        try:
            return json.load(urlopen(url))
        except URLError:
            sleep(i)
    raise URLError('urlopen timeout max retries')

def weather_for_url(url):
    return _parse_json(_json_for_url(url))

def jsonify(weather_data):
    row_string = ("{{date: new Date({date}), icon: '{icon}', icon_pos: {icon_pos}, " +
        "temp: {temp}, pop: {pop}, feel: {feel}, temp_c: {temp_c}, feel_c: {feel_c}}}")
    stringified = [row_string.format(**row) for row in weather_data]
    return "[" + ",\n".join(stringified) + "]"
        
if __name__ == "__main__":
    url = '/q/zmw:10027.1.99999'
    print jsonify(weather_for_url(url)[:12])