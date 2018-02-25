from datetime import datetime

from app import db


class Location(db.Model):
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    cache = db.Column(db.String)
    last_updated = db.Column(db.DateTime)

    def __init__(self, url, name, cache=''):
        self.url = url
        self.name = name
        self.cache = cache
        self.last_updated = (datetime.now() if cache
                             else datetime.fromtimestamp(0))

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


if __name__ == '__main__':
    db.create_all()