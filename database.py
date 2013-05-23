from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Location(db.Model):
    zipcode = db.Column(db.String, primary_key=True)
    city = db.Column(db.String)
    cache = db.Column(db.String)
    last_updated = db.Column(db.DateTime)
    def __init__(self, zipcode, city='', cache=''):
        self.zipcode = zipcode
        self.city = city
        self.cache = cache
        self.last_updated = datetime.now() if cache else datetime.fromtimestamp(0)
    def __repr__(self):
        return '<Zipcode %r, %r>' % (self.zipcode, self.city)

class Lookup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    zipcode = db.Column(db.String, db.ForeignKey('location.zipcode'))
    location = db.relationship('Location', backref=db.backref('lookups', lazy='dynamic'))
    def __init__(self, location):
        self.date = datetime.now()
        self.location = location
    def __repr__(self):
        return '<Lookup %r, %r>' % (self.zipcode, self.date)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    text = db.Column(db.String)
    def __init__(self, text):
        self.date = datetime.now()
        self.text = text
    def __repr__(self):
        return '<Comment %r, %r>' % (self.date, self.text)
