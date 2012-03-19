from urllib2 import urlopen
from json import load, dump
from os.path import dirname, abspath, getmtime, exists
from time import time

directory = dirname(abspath(__file__))
KEY = open(directory + '/key.txt', 'r').read().strip()
feature = 'hourly10day'
url_base = 'http://api.wunderground.com/api/%s/%s/q/%s.json'

def geolookup(zip_code):
    try:
        url = url_base % (KEY, 'geolookup', zip_code)
        return load(urlopen(url))['location']['city']
    except:
        return str(zip_code)

def weather_for_zip(zip_code):
    cache_file = dirname(abspath(__file__)) + '/cache/' + str(zip_code) + '.json'
    if exists(cache_file) and (time() - getmtime(cache_file))/60 < 45:
        data = load(open(cache_file))
    else:
        url = url_base % (KEY, feature, zip_code)
        data = load(urlopen(url))
        dump(data, open(cache_file, 'w')) 
    return data

def get_shit_i_care_about(w, num_hours):
    if not 'hourly_forecast' in w or not w['hourly_forecast']:
        return ''
    rows = []
    icon_pos = 100
    for i,f in enumerate(w['hourly_forecast'][0:num_hours]):
        icon = f['icon_url']
        time = int(f['FCTTIME']['epoch'])*1000  # date and time
        temp = f['temp']['english']             # temperature
        feels_like = f['feelslike']['english']  # temperature it feels like
        pop = f['pop']                          # percentage chance precipitation
        row = "{date: new Date(%d),\n icon: '%s', icon_pos: %s, temp: %s, pop: %s, feel: %s}" % \
                (time, icon, icon_pos, temp, pop, feels_like)
        rows.append(row)
    return "[" + ",\n".join(rows) + "]"
        
if __name__ == "__main__":
    w = weather_for_zip(10025)
    print get_shit_i_care_about(w,10)
