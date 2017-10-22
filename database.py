from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Location(db.Model):
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    cache = db.Column(db.String)
    last_updated = db.Column(db.DateTime)
    country = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zipcode = db.Column(db.String)

    def __init__(self, url, cache='', country='', city='', state='',
                 zipcode='', name=''):
        self.url = url
        self.cache = cache
        self.last_updated = (datetime.now() if cache
                             else datetime.fromtimestamp(0))
        self.country = country
        self.city = city
        self.state = state
        self.zipcode = zipcode
        if name:
            self.name = name
        else:
            if zipcode and state:
                self.name = '%s -- %s, %s' % (zipcode, city, state)
            else:
                self.name = '%s, %s' % (city, country)

    def __repr__(self):
        return '<Location %r, %r>' % (self.name, self.url)


class Lookup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    user_input = db.Column(db.String, index=True)
    name = db.Column(db.String, db.ForeignKey('location.name'))
    location = db.relationship('Location',
                               backref=db.backref('lookups', lazy='dynamic'))

    def __init__(self, user_input, location):
        self.date = datetime.now()
        self.user_input = user_input
        self.location = location

    def __repr__(self):
        return '<Lookup %r, %r, %r>' % (self.user_input, self.name, self.date)
