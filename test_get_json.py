import get_json

fake_json = {"hourly_forecast": [
	{
		"temp": { "metric": "28", "english": "83" },
	    "feelslike": { "metric": "28", "english": "83" },
	    "icon_url": "fake_url",
	    "pop": "0",
	    "FCTTIME": { "epoch": "1498165200", },
    },
    {
	    "temp": { "metric": "27", "english": "81" },
	    "feelslike": { "metric": "27", "english": "81" },
	    "icon_url": "fake_url",
	    "pop": "0",
	    "FCTTIME": { "epoch": "1498168800", },
    },
]}

def test_parse_json_english():
    actual = get_json._parse_json(fake_json)
    expected1 = ("{date: new Date(1498165200000),\n " +
    	"icon: 'fake_url', icon_pos: 100, temp: 83, pop: 0, feel: 83}")
    expected2 = ("{date: new Date(1498168800000),\n " +
    	"icon: 'fake_url', icon_pos: 100, temp: 81, pop: 0, feel: 81}")
    assert actual == [expected1, expected2]

def test_parse_json_metric():
    actual = get_json._parse_json(fake_json, 'C')
    expected1 = ("{date: new Date(1498165200000),\n " +
    	"icon: 'fake_url', icon_pos: 100, temp: 28, pop: 0, feel: 28}")
    expected2 = ("{date: new Date(1498168800000),\n " +
    	"icon: 'fake_url', icon_pos: 100, temp: 27, pop: 0, feel: 27}")
    assert actual == [expected1, expected2]