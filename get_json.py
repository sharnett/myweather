from urllib2 import urlopen
from json import load
import numpy as np
from scipy.interpolate import interp1d

KEY = open('/Users/srharnett/Dropbox/hacking/myweather/key.txt', 'r').read().strip()
feature = 'hourly7day'
url_base = 'http://api.wunderground.com/api/%s/%s/q/%s.json'

def weather_for_zip(zip_code):
    url = url_base % (KEY, feature, zip_code)
    return load(urlopen(url))

def interpolate(time, temp, feels_like, pop):
    t = np.linspace(time[0], time[-1])
    x1 = interp1d(time, temp, kind='cubic')
    x2 = interp1d(time, feels_like, kind='cubic')
    x3 = interp1d(time, pop, kind='cubic')
    return t,x1(t),x2(t),x3(t)

def get_shit_i_care_about(w, num_hours):
    if not 'hourly_forecast' in w or not w['hourly_forecast']:
        return ''
    rows, time, temp, feels_like, pop = [],[],[],[],[]
    for i,f in enumerate(w['hourly_forecast'][0:num_hours]):
        time += [int(f['FCTTIME']['epoch'])*1000]  # date and time
        temp += [f['temp']['english']]             # temperature
        feels_like += [f['feelslike']['english']]  # temperature it feels like
        pop += [f['pop']]                          # percentage chance precipitation
    if num_hours < 100:
        time,temp,feels_like,pop = interpolate(time, temp, feels_like, pop)
    for i in range(len(time)):
        row = "[new Date(%d), %s, %s, %s]" % (time[i], temp[i], feels_like[i], pop[i])
        rows.append(row)
    return ",\n".join(rows)
        
if __name__ == "__main__":
    w = weather_for_zip(10025)
    print get_shit_i_care_about(w,1000)
