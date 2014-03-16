#!/usr/bin/python
from get_json import weather_for_zip
from datetime import datetime
from json import dumps
from sqlite3 import connect
from os.path import dirname, abspath

if __name__ == '__main__':
    directory = dirname(abspath(__file__))
    conn = connect(directory + '/db.db')
    c = conn.cursor()
    zipcodes = {'10025', '10027', '10010', '11211'}
    for z in zipcodes:
        cache = dumps(weather_for_zip(z))
        last_updated = datetime.now()
        c.execute('update location set cache=?,last_updated=? where zipcode=?',
                (cache, last_updated, z))
    conn.commit()
    conn.close()
