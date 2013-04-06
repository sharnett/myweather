from urllib2 import urlopen
from json import load, dump
from os.path import dirname, abspath, getmtime, exists
from time import time

directory = dirname(abspath(__file__))
KEY = open(directory + '/key.txt', 'r').read().strip()
feature = 'hourly10day'
url_base = 'http://api.wunderground.com/api/%s/%s/q/%s.json'

def increment_zipcode(zip_code):
    cache_file = dirname(abspath(__file__)) + '/cache/zipcode_counts.json'
    cache = load(open(cache_file))
    if zip_code in cache:
        cache[zip_code] += 1
    else:
        cache[zip_code] = 1
    dump(cache, open(cache_file, 'w'))

def geolookup(zip_code):
    cache_file = dirname(abspath(__file__)) + '/cache/geo_lookups.json'
    cache = load(open(cache_file))
    if zip_code in cache:
        city = cache[zip_code]
    else:
        try:
            url = url_base % (KEY, 'geolookup', zip_code)
            city = load(urlopen(url))['location']['city']
        except:
            city = zip_code
        cache[zip_code] = city
        dump(cache, open(cache_file, 'w'))
    return city

def weather_for_zip(zip_code, check_cache=True):
    if check_cache:
        increment_zipcode(zip_code)
    cache_file = dirname(abspath(__file__)) + '/cache/' + zip_code + '.json'
    if check_cache and exists(cache_file) and (time() - getmtime(cache_file))/60 < 45:
        data = load(open(cache_file))
    else:
        url = url_base % (KEY, feature, zip_code)
        data = load(urlopen(url))
        dump(data, open(cache_file, 'w')) 
    return data

def get_shit_i_care_about(w, num_hours):
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
    rows = [get_row(f) for f in w['hourly_forecast'][0:num_hours]]
    return "[" + ",\n".join(rows) + "]"
        
if __name__ == "__main__":
    zip_code = '10025'
    w = weather_for_zip(zip_code)
    print get_shit_i_care_about(w,10)
    print geolookup(zip_code)
