import flask
import logging
import logging.handlers
from flask import render_template, request, session
from get_json import weather_for_url, parse_user_input, limit_hours
from re import match
from traceback import format_exc
from os import environ
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


@app.route('/', methods=['GET'])
def home():
    log.info('STARTING')
    user_input = request.args.get('user_input',
                                  session.get('user_input', '10027'))
    location, user_input = get_location(user_input)
    log.info('%s' % location)
    try:
        num_hours = int(request.args.get('num_hours', session.get('num_hours', 12)))
    except:
        flask.flash('seanweather didnt like the number of hours, using 12')
        num_hours = 12
    if (datetime.now()-location.last_updated).seconds > 2700 or len(location.cache) == 0:
        log.info('using weather API for %s' % location.zmw)
        location.cache = dumps(weather_for_url(location.url))
        location.last_updated = datetime.now()
    else:
        log.info('weather for %s was recently cached, reusing' % location.zmw)
    ds = limit_hours(loads(location.cache), num_hours)
    location = db.session.merge(location)
    db.session.add(Lookup(user_input, location))
    db.session.commit()
    session['user_input'] = user_input
    session['num_hours'] = num_hours
    session.permanent = True
    log.info('FINISHED with %s' % user_input)
    return render_template('weather_form.html', data_string=ds, city=location.name, 
            user_input=user_input, num_hours=num_hours)


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
