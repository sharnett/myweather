import flask
from flask import render_template, request, session
from get_json import *
from re import match
from traceback import format_exc
from os import environ

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
app.config.from_object(__name__)

def main():
    app.run(host='0.0.0.0')

@app.route('/', methods=['GET'])
def home():
    prev_zip = session.get('zip_code', '10027')
    try:
        zip_code = request.args.get('zip_code', prev_zip)
        assert(match(r'^\d{5}$', zip_code))
    except:
        zip_code = '10025'
    try:
        num_hours = int(request.args.get('num_hours', session.get('num_hours', 12)))
    except:
        num_hours = 12
    if zip_code == prev_zip:
        city = session.get('city', geolookup(zip_code)) 
    else:
        city = geolookup(zip_code)
    session['zip_code'] = zip_code
    session['num_hours'] = num_hours
    session['city'] = city
    w = weather_for_zip(zip_code)
    ds = get_shit_i_care_about(w, num_hours)
    return render_template('weather_form.html', data_string=ds, city=city, 
            zip_code=zip_code, num_hours=num_hours)

@app.route('/lunch')
def lunch():
    return render_template('lunch.html')

if __name__ == '__main__':
    main()
