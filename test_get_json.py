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
    actual = get_json.parse_json(fake_json)
    expected1 = ("{date: new Date(1498165200000),\n " +
    	"icon: 'fake_url', icon_pos: 100, temp: 83, pop: 0, feel: 83}")
    expected2 = ("{date: new Date(1498168800000),\n " +
    	"icon: 'fake_url', icon_pos: 100, temp: 81, pop: 0, feel: 81}")
    expected = [expected1, expected2]
    assert actual == expected

def test_parse_json_metric():
    actual = get_json.parse_json(fake_json, 'metric')
    expected1 = ("{date: new Date(1498165200000),\n " +
    	"icon: 'fake_url', icon_pos: 100, temp: 28, pop: 0, feel: 28}")
    expected2 = ("{date: new Date(1498168800000),\n " +
    	"icon: 'fake_url', icon_pos: 100, temp: 27, pop: 0, feel: 27}")
    expected = [expected1, expected2]
    assert actual == expected   