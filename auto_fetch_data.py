#!/usr/bin/python
from get_json import weather_for_zip
from time import asctime
from os.path import dirname, abspath

if __name__ == '__main__':
    zipcodes = {'10025', '10027', '10010', '10016'}
    for z in zipcodes:
        weather_for_zip(z, check_cache=False)
    directory = dirname(abspath(__file__))
    open(directory + '/timelog.txt', 'a').write(asctime()+'\n')
