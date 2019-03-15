from urllib2 import URLError
import json
import pytest
import time

import app.wunderground as wunderground

fake_json = {"list": [
    {u'dt': 1552942800,
     u'main': {u'humidity': 82,
               u'temp': 292.445,
               u'temp_max': 282.445,
               u'temp_min': 282.445},
     u'rain': {},
     u'weather': [{u'icon': u'fake_icon',}]},
    {u'dt': 1552949900,
     u'main': {u'humidity': 85,
               u'temp': 295.445,
               u'temp_max': 282.445,
               u'temp_min': 282.445},
     u'rain': {u'3h': 0.01},
     u'weather': [{u'icon': u'fake_icon',}]},
]}

paris = {"RESULTS": [
    {
        "name": "Paris, France",
        "type": "city",
        "c": "FR",
        "zmw": "00000.45.07156",
        "tz": "Europe / Paris",
        "tzs": "CET",
        "l": "/q/zmw:00000.45.07156",
        "ll": "48.860001 2.350000",
        "lat": "48.860001",
        "lon": "2.350000"
    },
]}

def test_parse_json():
    actual = wunderground._parse_json(fake_json)
    expected1 = dict(date=1552942800000, icon=u'http://openweathermap.org/img/w/fake_icon.png', icon_pos=10,
                     temp='67', pop='0.0', feel='67', temp_c='19', feel_c='19')
    expected2 = dict(date=1552949900000, icon=u'http://openweathermap.org/img/w/fake_icon.png', icon_pos=10,
                     temp='72', pop='0.0', feel='72', temp_c='22', feel_c='22')
    assert actual == [expected1, expected2]


def test_autocomplete_user_input():
    class fake:
        def read(self):
            return json.dumps(paris)
    url, name = wunderground.autocomplete_user_input('paris', lambda url: fake())
    assert url == '/q/zmw:00000.45.07156'
    assert name == 'Paris, France'


def test_json_for_location(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda seconds: None)
    def fake_opener(url):
        raise URLError('Generic fail message')

    with pytest.raises(URLError) as excinfo:
        wunderground._json_for_location('paris', 'real_api_key', fake_opener)
    assert 'urlopen error urlopen timeout max retries' in str(excinfo.value)