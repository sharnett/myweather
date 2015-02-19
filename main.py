import flask
import logging
import logging.handlers
from flask import render_template, request, session
from get_json import weather_for_zip, geolookup, limit, get_location
from re import match
from traceback import format_exc
from os import environ
from database import db, Location, Lookup, Comment
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

@app.route('/', methods=['GET'])
def home():
    log.info('STARTING')
    prev_zip = session.get('zipcode', '10027')
    try:
        zipcode = request.args.get('zipcode', prev_zip)
        assert(match(r'^\d{5}$', zipcode))
        log.info('got %s from the request or session' % zipcode)
    except:
        log.info('%s doesnt look like a zipcode, trying to parse' % zipcode)
        zipcode = get_location(zipcode)
        if zipcode is None:
            zipcode = '10027'
            log.info('couldnt parse location, using %s' % zipcode)
        else:
            log.info('%s parsed' % zipcode)
    try:
        num_hours = int(request.args.get('num_hours', session.get('num_hours', 12)))
    except:
        num_hours = 12
    location = Location.query.get(zipcode)
    if not location:
        log.info('%s wasnt in the cache, looking up geo information' % zipcode)
        location = Location(zipcode, geolookup(zipcode))
    else:
        log.info('%s was in the cache, reusing geoinformation' % zipcode)
    log.info('%s is %s' % (zipcode, location.city))
    if (datetime.now()-location.last_updated).seconds > 2700 or len(location.cache) == 0:
        log.info('looking up the weather for %s' % zipcode)
        location.cache = dumps(weather_for_zip(zipcode))
        location.last_updated = datetime.now()
    else:
        log.info('weather for %s was recently cached, reusing' % zipcode)
    ds = limit(loads(location.cache), num_hours)
    location = db.session.merge(location)
    db.session.add(Lookup(location))
    db.session.commit()
    session['zipcode'] = zipcode
    session['num_hours'] = num_hours
    log.info('FINISHED with %s' % zipcode)
    return render_template('weather_form.html', data_string=ds, city=location.city, 
            zipcode=zipcode, num_hours=num_hours)

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
