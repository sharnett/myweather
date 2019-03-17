from datetime import datetime

from app import db
from wunderground import Location


class Lookup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    user_input = db.Column(db.String, index=True)
    location_id = db.Column(db.Integer)
    location_name = db.Column(db.String)
    location_country = db.Column(db.String)

    def __init__(self, user_input, location):
        self.date = datetime.now()
        self.user_input = user_input
        self.location_id = location.location_id
        self.location_name = location.name
        self.location_country = location.country

    def __repr__(self):
        return '<Lookup %r, %r, %r>' % (self.user_input, self.location_name, self.date)


if __name__ == '__main__':
    db.create_all()
