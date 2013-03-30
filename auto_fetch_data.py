#!/usr/bin/python
from get_json import weather_for_zip
from time import asctime
from os.path import dirname, abspath

if __name__ == '__main__':
    zipcodes = {'10025', '10027', '02139', '94110'}
    for z in zipcodes:
        weather_for_zip(z)
    directory = dirname(abspath(__file__))
    open(directory + 'timelog.txt', 'a').write(asctime()+'\n')
