import flask
import logging
import logging.handlers
import re
from flask import render_template, request, session
from get_json import weather_for_url, parse_user_input, limit_hours
from os import environ
from os.path import dirname, abspath, isfile
from database import db, Location, Lookup
from datetime import datetime
from json import loads, dumps

app = flask.Flask(__name__)
SECRET_KEY = environ.get('SECRET_KEY', 'development')
DEBUG = True if SECRET_KEY == 'development' else False
if not DEBUG:
    import logging
    from TlsSMTPHandler import TlsSMTPHandler
    from email_credentials import email_credentials
    mail_handler = TlsSMTPHandler(*email_credentials())
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.db'
app.config.from_object(__name__)
db.init_app(app)

log = logging.getLogger('seanweather')
log.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler('seanweather.log', maxBytes=10000000)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

if not isfile(dirname(abspath(__file__)) + '/db.db'):
    log.warning('db doesnt exist, creating a new one')
    with app.app_context():
        db.create_all()


def main():
    app.run(host='0.0.0.0')


def get_location(user_input):
    ''' first check cache. if missing or too old, use autocomplete API '''
    last_lookup = Lookup.query.filter_by(user_input=user_input).order_by(Lookup.date.desc()).first()
    log.info('db result for location: ' + str(last_lookup))
    if last_lookup is not None and (datetime.now()-last_lookup.date).seconds < 604800:
        log.info('got location info from the cache')
        return last_lookup.location, user_input
    try:
        url, location_name, zmw = parse_user_input(user_input)
        log.info('got location info from autocomplete API')
        log.info('%s -> %s, %s, %s' % (user_input, url, location_name, zmw))
        return Location(zmw, url=url, name=location_name), user_input
    except IndexError, KeyError:
        flask.flash('seanweather didnt like that, please try another city or zipcode')
        log.warning('failed to parse: %s. Using 10027' % user_input)
        last_default = Lookup.query.filter_by(user_input='10027').order_by(Lookup.date.desc()).first()
        if last_default is not None:
            location = last_default.location
        else:
            url, location_name, zmw = '/q/zmw:10027.1.99999', '10027 - New York, NY', '10027.1.99999'
            location = Location(zmw, url=url, name=location_name)
        return location, '10027'


def parse_temps(weather_data, num_hours=24):
    temps = []
    pattern = r'temp: (\d+)'
    for d in weather_data[:num_hours]:
        m = re.search(pattern, d)
        if m is not None:
            temps.append(int(m.group(1)))
    if not temps:
        return '', '', ''
    return temps[0], max(temps), min(temps)

def parse_icon(weather_data):
    pattern = r"icon: ('.*'),"
    m = re.search(pattern, weather_data[0])
    if m is not None:
        return m.group(1)
    return ''

@app.route('/', methods=['GET'])
def home():
    log.info('STARTING')
    # units
    units = session.get('units', 'F')
    if request.args.get('toggle_units') == 'true':
        units = 'C' if units == 'F' else 'F'
    session['units'] = units

    # zip code
    user_input = request.args.get('user_input',
                                  session.get('user_input', '10027'))
    location, user_input = get_location(user_input)
    log.info('%s' % location)

    # number of hours
    try:
        num_hours = int(request.args.get('num_hours', session.get('num_hours', 12)))
    except:
        flask.flash('seanweather didnt like the number of hours, using 12')
        num_hours = 12

    if (datetime.now()-location.last_updated).seconds > 2700 or len(location.cache) == 0:
        log.info('using weather API for %s' % location.zmw)
        wd = weather_for_url(location.url, units)
        location.cache = dumps(wd)
        if wd:
            location.last_updated = datetime.now()
        else:
            log.warning("didn't get any results from weather API")
    else:
        log.info('weather for %s was recently cached, reusing' % location.zmw)
    location = db.session.merge(location)
    db.session.add(Lookup(user_input, location))
    db.session.commit()

    weather_data = loads(location.cache)
    current_temp, max_temp, min_temp = parse_temps(weather_data)
    icon = parse_icon(weather_data)
    ds = limit_hours(weather_data, num_hours)
    session['user_input'] = user_input
    session['num_hours'] = num_hours
    session.permanent = True
    log.info('FINISHED with %s' % user_input)
    return render_template('weather_form.html', data_string=ds,
                           location=location.name, user_input=user_input,
                           num_hours=num_hours, current_temp=current_temp,
                           max_temp=max_temp, min_temp=min_temp, icon=icon, units=units)

@app.route('/fake')
def fake():
    log.info('STARTING -- fake')
    ds = '''[{date: new Date(1461434400000),
 icon: 'http://icons.wxug.com/i/c/k/partlycloudy.gif', icon_pos: 100, temp: 66, pop: 15, feel: 66},
{date: new Date(1461438000000),
 icon: 'http://icons.wxug.com/i/c/k/partlycloudy.gif', icon_pos: 100, temp: 67, pop: 15, feel: 67},
{date: new Date(1461441600000),
 icon: 'http://icons.wxug.com/i/c/k/partlycloudy.gif', icon_pos: 100, temp: 67, pop: 15, feel: 67},
{date: new Date(1461445200000),
 icon: 'http://icons.wxug.com/i/c/k/partlycloudy.gif', icon_pos: 100, temp: 68, pop: 15, feel: 68},
{date: new Date(1461448800000),
 icon: 'http://icons.wxug.com/i/c/k/clear.gif', icon_pos: 100, temp: 66, pop: 0, feel: 66},
{date: new Date(1461452400000),
 icon: 'http://icons.wxug.com/i/c/k/clear.gif', icon_pos: 100, temp: 64, pop: 0, feel: 64},
{date: new Date(1461456000000),
 icon: 'http://icons.wxug.com/i/c/k/nt_clear.gif', icon_pos: 100, temp: 62, pop: 0, feel: 62},
{date: new Date(1461459600000),
 icon: 'http://icons.wxug.com/i/c/k/nt_clear.gif', icon_pos: 100, temp: 61, pop: 0, feel: 61},
{date: new Date(1461463200000),
 icon: 'http://icons.wxug.com/i/c/k/nt_clear.gif', icon_pos: 100, temp: 59, pop: 0, feel: 59},
{date: new Date(1461466800000),
 icon: 'http://icons.wxug.com/i/c/k/nt_clear.gif', icon_pos: 100, temp: 58, pop: 0, feel: 58},
{date: new Date(1461470400000),
 icon: 'http://icons.wxug.com/i/c/k/nt_clear.gif', icon_pos: 100, temp: 55, pop: 0, feel: 55},
{date: new Date(1461474000000),
 icon: 'http://icons.wxug.com/i/c/k/nt_clear.gif', icon_pos: 100, temp: 53, pop: 0, feel: 53}]'''
    icon = 'http://icons.wxug.com/i/c/k/nt_clear.gif'
    location = '10027 -- New York, NY'
    user_input = 'chilled'
    num_hours = 12
    current_temp, max_temp, min_temp = 75, 80, 65
    units = 'F'
    log.info('FINISHED with %s -- fake' % user_input)
    return render_template('weather_form.html', data_string=ds,
                           location=location, user_input=user_input,
                           num_hours=num_hours, current_temp=current_temp,
                           max_temp=max_temp, min_temp=min_temp, icon=icon, units=units)


@app.route('/comment', methods=['POST'])
def comment():
    text = request.form['comment']
    if text:
        db.session.add(Comment(text))
        db.session.commit()
        flask.flash('We appreciate your feedback! :)')
    return flask.redirect(flask.url_for('home'))


@app.route('/discuss')
def discuss():
    return render_template('discuss.html')

if __name__ == '__main__':
    main()
