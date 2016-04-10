import logging
import urllib
from urllib2 import urlopen, URLError
from json import load, dump
from os.path import dirname, abspath, getmtime, exists
from os import environ
from time import time, sleep

logging.basicConfig()
log = logging.getLogger(__name__)
directory = dirname(abspath(__file__))
KEY = environ['WUNDERGROUND_KEY']
feature = 'hourly10day'
url_base = 'http://api.wunderground.com/api/%s/%s/q/%s.json'
url_base2 = 'http://api.wunderground.com/api/%s/%s%s.json'

def geolookup(zip_code):
    url = url_base % (KEY, 'geolookup', zip_code)
    try:
        x = load(urlopen(url))['location']
    except:
        return zip_code
    try:
        city = x['city']
    except:
        return zip_code
    try:
        state = x['state']
    except:
        print('boner')
        return city
    return city + ', ' + state

def get_shit_i_care_about(w):
    if not 'hourly_forecast' in w or not w['hourly_forecast']:
        return ''
    def get_row(f):
        icon_pos = 100
        icon = f['icon_url']
        time = int(f['FCTTIME']['epoch'])*1000  # date and time
        temp = f['temp']['english']             # temperature
        feels_like = f['feelslike']['english']  # temperature it feels like
        pop = f['pop']                          # probability of precipitation
        return "{date: new Date(%d),\n icon: '%s', icon_pos: %s, temp: %s, pop: %s, feel: %s}" % \
                (time, icon, icon_pos, temp, pop, feels_like)
    return [get_row(f) for f in w['hourly_forecast']]

def parse_user_input(s):
    ''' Takes contents of 'enter zip code or city' field and gives it to the wunderground autocomplete API.
    Returns the URL path and name of the top result.
    '''
    url = 'http://autocomplete.wunderground.com/aq?query=%s' % urllib.quote(s)
    try:
        top_result = load(urlopen(url))['RESULTS'][0]
        return top_result['l'], top_result['name'], top_result['zmw']
    except:
        log.warning("Couldn't get location for %s" % s)
        return None, None, None

def weather_for_url(url):
    url = url_base2 % (KEY, feature, url)
    for i in range(3):
        try:
            data = load(urlopen(url))
            break
        except URLError:
            sleep(i)
    else:
        raise URLError('urlopen timeout max retries')
    return get_shit_i_care_about(data)

def weather_for_zip(zip_code):
    url = url_base % (KEY, feature, zip_code)
    for i in range(3):
        try:
            data = load(urlopen(url))
            break
        except URLError:
            sleep(i)
    else:
        raise URLError('urlopen timeout max retries')
    return get_shit_i_care_about(data)

def limit(g, num_hours):
    rows = g[:num_hours]
    return "[" + ",\n".join(rows) + "]"
        
if __name__ == "__main__":
    zip_code = '10025'
    print limit(weather_for_zip(zip_code), 12)
    print geolookup(zip_code)
