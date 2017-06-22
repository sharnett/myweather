import logging
import urllib
from urllib2 import urlopen, URLError
from json import load
from os import environ
from time import time, sleep

logging.basicConfig()
log = logging.getLogger(__name__)
KEY = environ['WUNDERGROUND_KEY']
feature = 'hourly10day'
url_base = 'http://api.wunderground.com/api/%s/%s%s.json'

def _parse_json(json_data, units='english'):
    w = json_data
    if not 'hourly_forecast' in w or not w['hourly_forecast']:
        return ''
    def get_row(f):
        icon_pos = 100
        icon = f['icon_url']
        time = int(f['FCTTIME']['epoch'])*1000  # date and time
        temp = f['temp'][units]             # temperature
        feels_like = f['feelslike'][units]  # temperature it feels like
        pop = f['pop']                          # probability of precipitation
        return "{date: new Date(%d),\n icon: '%s', icon_pos: %s, temp: %s, pop: %s, feel: %s}" % \
                (time, icon, icon_pos, temp, pop, feels_like)
    return [get_row(f) for f in w['hourly_forecast']]

def parse_user_input(s):
    ''' Takes contents of 'enter zip code or city' field and gives it to the wunderground autocomplete API.
    Returns the URL path and name of the top result.
    '''
    url = 'http://autocomplete.wunderground.com/aq?query=%s' % urllib.quote(s)
    response = load(urlopen(url))
    # will raise an IndexError if RESULTS is empty
    top_result = response['RESULTS'][0]
    logging.info(top_result['l'])
    return top_result['l'], top_result['name'], top_result['zmw']
  
def _json_for_url(url):
    url = url_base % (KEY, feature, url)
    for i in range(3):
        try:
            json_data = load(urlopen(url))
            break
        except URLError:
            sleep(i)
    else:
        raise URLError('urlopen timeout max retries')
    return json_data

def weather_for_url(url):
    return _parse_json(_json_for_url(url))

def limit_hours(g, num_hours):
    rows = g[:num_hours]
    return "[" + ",\n".join(rows) + "]"
        
if __name__ == "__main__":
    url = '/q/zmw:10027.1.99999'
    print limit_hours(weather_for_url(url), 12)