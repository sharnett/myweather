#!/usr/bin/python
from get_json import weather_for_url
from datetime import datetime
from json import dumps
from sqlite3 import connect
from os.path import dirname, abspath

if __name__ == '__main__':
    directory = dirname(abspath(__file__))
    conn = connect(directory + '/db.db')
    c = conn.cursor()
    zipcodes = {'10003', '12180', '11105', '11215'}
    for z in zipcodes:
        zmw = '%s.1.99999' % z
        url = '/q/zmw:%s' % zmw
        cache = dumps(weather_for_url(url))
        last_updated = datetime.now()
        c.execute('update location set cache=?, last_updated=? where zmw=?',
                (cache, last_updated, zmw))

    conn.commit()
    conn.close()
