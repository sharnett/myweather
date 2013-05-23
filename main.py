import flask
from flask import render_template, request, session
from get_json import weather_for_zip, geolookup, limit
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

def main():
    app.run(host='0.0.0.0')

@app.route('/', methods=['GET'])
def home():
    prev_zip = session.get('zipcode', '10027')
    try:
        zipcode = request.args.get('zipcode', prev_zip)
        assert(match(r'^\d{5}$', zipcode))
    except:
        zipcode = '10027'
    try:
        num_hours = int(request.args.get('num_hours', session.get('num_hours', 12)))
    except:
        num_hours = 12
    location = Location.query.get(zipcode)
    if not location:
        location = Location(zipcode, geolookup(zipcode))
    if (datetime.now()-location.last_updated).seconds > 2700:
        location.cache = dumps(weather_for_zip(zipcode))
        location.last_updated = datetime.now()
    ds = limit(loads(location.cache), num_hours)
    location = db.session.merge(location)
    db.session.add(Lookup(location))
    db.session.commit()
    session['zipcode'] = zipcode
    session['num_hours'] = num_hours
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

if __name__ == '__main__':
    main()
