from urllib2 import urlopen
from json import load, dump
from os.path import dirname, abspath, getmtime, exists
from datetime import datetime

def weather_for_zip(zip_code, feature = 'yesterday'):
    directory = dirname(abspath(__file__))
    KEY = open(directory + '/key.txt', 'r').read().strip()
    url_base = 'http://api.wunderground.com/api/%s/%s/q/%s.json'
    url = url_base % (KEY, feature, zip_code)
    data = load(urlopen(url))
    return data

def today_goodness(w, verbose=False):
    ''' returns False if weather between first and last hour contains rain or
    'feels like' temperature above 90F'''
    MIN_TEMP, MAX_TEMP = 67, 93
    if not 'history' in w or not w['history']:
        raise Exception('weather dictionary malformed')
    good = True
    obs = w['history']['observations'][first:last+1]
    for ob in obs:
        t = float(ob['heatindexi'])
        if t == -9999: t = float(ob['tempi'])
        rain = ob['rain']
        if verbose: 
            print ob['date']['pretty']
            print 'feels like', t, 'rain', rain
        if t>MAX_TEMP or t<MIN_TEMP or rain=='1':
            good = False
    return good

def yesterday_goodness(w, verbose=False, MIN_TEMP=67, MAX_TEMP=93):
    first, last = 10, 13
    ''' returns False if weather between first and last hour contains rain or
    'feels like' temperature above or below limits'''
    if not 'history' in w or not w['history']:
        raise Exception('weather dictionary malformed')
    good = True
    obs = w['history']['observations'][first:last+1]
    for ob in obs:
        t = float(ob['heatindexi'])
        if t < -99: t = float(ob['tempi'])
        rain = ob['rain']
        if verbose: 
            print ob['date']['pretty']
            print 'feels like', t, 'rain', rain
        if t>MAX_TEMP or t<MIN_TEMP or rain=='1':
            good = False
    return good

def get_last_taco():
    d = datetime.strptime(open('taco.txt').read().strip(), '%Y%m%d')
    return d
        
if __name__ == "__main__":
    zip_code = 10027
    w = weather_for_zip(zip_code)
    print determine_goodness(w)
