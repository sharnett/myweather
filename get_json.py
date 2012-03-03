from urllib2 import urlopen
from json import load

KEY = open('/home/sean/myweather/key.txt', 'r').read().strip()
feature = 'hourly7day'
url_base = 'http://api.wunderground.com/api/%s/%s/q/%s.json'

def weather_for_zip(zip_code):
    url = url_base % (KEY, feature, zip_code)
    return load(urlopen(url))

def get_shit_i_care_about(w, num_hours):
    rows = []
    if not 'hourly_forecast' in w or not w['hourly_forecast']:
        return ''
    for f in w['hourly_forecast'][0:num_hours]:
        time = int(f['FCTTIME']['epoch'])*1000  # date and time
        temp = f['temp']['english']             # temperature
        feels_like = f['feelslike']['english']  # temperature it feels like
        pop = f['pop']                          # percentage chance precipitation
        row = "[new Date(%d), %s, %s, %s]" % (time, temp, feels_like, pop)
        rows.append(row)
    return ",\n".join(rows)
        
if __name__ == "__main__":
    w = weather_for_zip(10025)
    print get_shit_i_care_about(w,1000)
