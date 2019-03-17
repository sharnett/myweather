import logging
import logging.handlers
import os
from os.path import dirname, abspath, isfile

SECRET_KEY = os.environ.get('SECRET_KEY', 'development')
API_KEY = os.environ.get('OPENWEATHERMAP_KEY', 'development')
DEBUG = True if SECRET_KEY == 'development' else False

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.db')

handlers = []
if DEBUG:
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)
else:
    from TlsSMTPHandler import TlsSMTPHandler
    from email_credentials import email_credentials
    mail_handler = TlsSMTPHandler(*email_credentials())
    mail_handler.setLevel(logging.ERROR)
    handlers.append(mail_handler)

log = logging.getLogger('seanweather')
log.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler('seanweather.log', maxBytes=10000000)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
handlers.append(fh)
for h in handlers:
    log.addHandler(h)
