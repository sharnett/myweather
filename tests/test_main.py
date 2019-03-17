import json
import pytest

from app.database import Lookup
from app.wunderground import Location
import app.main as seanweather

def test_jsonify():
    weather_data = [
    dict(
        date=1498165200000,
        icon="fake_url",
        icon_pos=100,
        pop=0,
        temp=83,
        temp_c=28,
        feel=83,
        feel_c=28),
    dict(
        date=1498168800000,
        icon="fake_url",
        icon_pos=100,
        pop=0,
        temp=81,
        temp_c=27,
        feel=81,
        feel_c=27)
    ]
    actual = seanweather.jsonify(weather_data)
    expected1 = ("{date: new Date(1498165200000), icon: 'fake_url', "
                 "icon_pos: 100, temp: 83, pop: 0, feel: 83, temp_c: 28, "
                 "feel_c: 28}")
    expected2 = ("{date: new Date(1498168800000), icon: 'fake_url', "
                 "icon_pos: 100, temp: 81, pop: 0, feel: 81, temp_c: 27, "
                 "feel_c: 27}")
    expected = '[' + expected1 + ',\n' + expected2 + ']'
    assert actual == expected


@pytest.fixture
def app():
    seanweather.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
    seanweather.app.config['TESTING'] = True
    return seanweather.app

@pytest.fixture
def db(app):
    seanweather.db.app = app
    seanweather.db.create_all()
    yield seanweather.db
    seanweather.db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()
    db.session = db.create_scoped_session(options=dict(bind=connection))

    yield db.session

    transaction.rollback()
    connection.close()
    db.session.remove()


########## SeanWeather.update_units ##############

def test_update_units_no_request(app):
    sw = seanweather.SeanWeather()
    sw.previous = seanweather.CookieData(units='C', user_input='', num_hours=0)
    with app.test_request_context(''):
        sw.update_units()
    assert sw.units == seanweather.Units.C

def test_update_units_request_invalid(app):
    ''' The new_units query parameter is often missing '''
    sw = seanweather.SeanWeather()
    sw.previous = seanweather.CookieData(units='C', user_input='', num_hours=0)
    with app.test_request_context('?new_units=&num_hours=24'):
        sw.update_units()
    assert sw.units == seanweather.Units.C

def test_update_units_request_same(app):
    sw = seanweather.SeanWeather()
    sw.previous = seanweather.CookieData(units='C', user_input='', num_hours=0)
    with app.test_request_context('?new_units=C'):
        sw.update_units()
    assert sw.units == seanweather.Units.C

def test_update_units_request_new(app):
    sw = seanweather.SeanWeather()
    sw.previous = seanweather.CookieData(units='C', user_input='', num_hours=0)
    with app.test_request_context('?new_units=F'):
        sw.update_units()
    assert sw.units == seanweather.Units.F


########## SeanWeather.update_num_hours ##############

def test_update_num_hours_bad_request(app):
    sw = seanweather.SeanWeather()
    sw.previous = seanweather.CookieData(units='', user_input='', num_hours='36')
    with app.test_request_context('?num_hours=tacos'):
        sw.update_num_hours()
    assert sw.num_hours == seanweather._DEFAULT_NUM_HOURS

def test_update_num_hours_good_request(app):
    sw = seanweather.SeanWeather()
    sw.previous = seanweather.CookieData(units='', user_input='', num_hours='36')
    with app.test_request_context('?num_hours=48'):
        sw.update_num_hours()
    assert sw.num_hours == 48


########## SeanWeather.update_weather_data ##############

def test_update_weather_data_empty_response(session, app):
    sw = seanweather.SeanWeather()
    sw.location = Location(0, 'NYC', 'US')
    fake_weather_getter = lambda url, api_key: ([], sw.location)
    with app.test_request_context('?user_input=foo'):
        sw.update_weather_data(weather_getter=fake_weather_getter)
    assert sw.weather_data == []

def test_update_weather_data_good_response(session, app):
    sw = seanweather.SeanWeather()
    sw.location = Location(0, 'NYC', 'US')
    weather_data = [dict(date=0, icon='', icon_pos=100, temp='100', pop='0',
                         feel='100', temp_c='35', feel_c='35')]*100
    fake_weather_getter = lambda url, api_key: (weather_data, sw.location)
    with app.test_request_context('?user_input=foo'):
        sw.update_weather_data(weather_getter=fake_weather_getter)
    assert sw.weather_data == weather_data


########## SeanWeather.update_current_conditions ##############

def _get_weather_data():
    weather_data = [{'temp': '83', 'temp_c': '28', 'icon': 'cloud'},
                    {'temp': '81', 'temp_c': '27', 'icon': 'sun'},
                    {'temp': '85', 'temp_c': '29'}]
    weather_data *= 10
    # The below two data points are outside the default 24-hour period, so they
    # should not be included in the max/min calculation
    weather_data.append({'temp': '100', 'temp_c': '100'})
    weather_data.append({'temp': '0', 'temp_c': '0'})
    return weather_data

def test_update_current_conditions_F():
    sw = seanweather.SeanWeather()
    sw.weather_data = _get_weather_data()

    sw.update_current_conditions()

    assert sw.current_temp == 83
    assert sw.max_temp == 85
    assert sw.min_temp == 81
    assert sw.icon == 'cloud'

def test_update_current_conditions_C():
    sw = seanweather.SeanWeather()
    sw.units = seanweather.Units.C
    sw.weather_data = _get_weather_data()

    sw.update_current_conditions()

    assert sw.current_temp == 28
    assert sw.max_temp == 29
    assert sw.min_temp == 27
    assert sw.icon == 'cloud'
