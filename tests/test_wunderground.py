from urllib2 import URLError
import json
import pytest
import time

import app.wunderground as wunderground

fake_json = {
        "city": {
            "id":5128581,
            "name":"New York",
            "country":"US"},
        "list": [
            {
                u'dt': 1552942800,
                u'main': {
                    u'humidity': 82,
                    u'temp': 292.445,
                    u'temp_max': 282.445,
                    u'temp_min': 282.445},
                u'rain': {},
                u'weather': [{u'icon': u'fake_icon',}]},
            {
                u'dt': 1552949900,
                u'main': {
                    u'humidity': 85,
                    u'temp': 295.445,
                    u'temp_max': 282.445,
                    u'temp_min': 282.445},
                u'rain': {u'3h': 0.01},
                u'weather': [{u'icon': u'fake_icon',}]},
            ]
        }

def test_parse_json():
    actual = wunderground._parse_json(fake_json)
    expected_location = wunderground.Location(5128581, 'New York', 'US')
    expected1 = dict(date=1552942800000, icon=u'http://openweathermap.org/img/w/fake_icon.png', icon_pos=10,
                     temp='67', pop='0.0', feel='67', temp_c='19', feel_c='19')
    expected2 = dict(date=1552949900000, icon=u'http://openweathermap.org/img/w/fake_icon.png', icon_pos=10,
                     temp='72', pop='0.0', feel='72', temp_c='22', feel_c='22')
    assert actual == ([expected1, expected2], expected_location)



def test_json_for_user_input(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda seconds: None)
    def fake_opener(url):
        raise URLError('Generic fail message')

    with pytest.raises(URLError) as excinfo:
        wunderground._json_for_user_input('paris', 'real_api_key', fake_opener)
    assert 'urlopen error urlopen timeout max retries' in str(excinfo.value)
