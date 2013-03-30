#!/usr/bin/python
from get_json import weather_for_zip

if __name__ == '__main__':
    zipcodes = {'10025', '10027', '02139', '94110'}
    for z in zipcodes:
        print z
        weather_for_zip(z)
