from urllib2 import URLError
import json
import pytest
import time

import wunderground

fake_json = {"hourly_forecast": [
    {
        "temp": {"metric": "28", "english": "83"},
        "feelslike": {"metric": "28", "english": "83"},
        "icon_url": "fake_url",
        "pop": "0",
        "FCTTIME": {"epoch": "1498165200"},
    },
    {
        "temp": {"metric": "27", "english": "81"},
        "feelslike": {"metric": "27", "english": "81"},
        "icon_url": "fake_url",
        "pop": "0",
        "FCTTIME": {"epoch": "1498168800"},
    },
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
    expected1 = dict(date=1498165200000, icon='fake_url', icon_pos=100,
                     temp='83', pop='0', feel='83', temp_c='28', feel_c='28')
    expected2 = dict(date=1498168800000, icon='fake_url', icon_pos=100,
                     temp='81', pop='0', feel='81', temp_c='27', feel_c='27')
    assert actual == [expected1, expected2]


def test_autocomplete_user_input():
    class fake:
        def read(self):
            return json.dumps(paris)
    url, name = wunderground.autocomplete_user_input('paris', lambda url: fake())
    assert url == '/q/zmw:00000.45.07156'
    assert name == 'Paris, France'


def test_json_for_url(monkeypatch):
    monkeypatch.setattr(time, 'sleep', lambda seconds: None)
    def fake_opener(url):
        raise URLError('Generic fail message')

    with pytest.raises(URLError) as excinfo:
        wunderground._json_for_url('url', 'real_api_key', fake_opener)
    assert 'urlopen error urlopen timeout max retries' in str(excinfo.value)