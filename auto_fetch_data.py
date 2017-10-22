#!/usr/bin/python
import os
from wunderground import weather_for_url
from datetime import datetime
from json import dumps
from sqlite3 import connect
from os.path import dirname, abspath

API_KEY = os.environ.get('WUNDERGROUND_KEY', 'development')

if __name__ == '__main__':
    directory = dirname(abspath(__file__))
    conn = connect(directory + '/db.db')
    c = conn.cursor()
    zipcodes = {'10003', '12180', '11105', '11215'}
    for z in zipcodes:
        url = '/q/zmw:%s.1.99999' % z
        cache = dumps(weather_for_url(url, API_KEY))
        last_updated = datetime.now()
        c.execute('update location set cache=?, last_updated=? where url=?',
                  (cache, last_updated, url))

    conn.commit()
    conn.close()
