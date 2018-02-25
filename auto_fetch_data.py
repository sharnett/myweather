import json
import os
import sqlalchemy

from config import API_KEY, SQLALCHEMY_DATABASE_URI
from app.database import Location
from app.wunderground import weather_for_url, autocomplete_user_input

def get_db_session():
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    return sqlalchemy.orm.sessionmaker(bind=engine)()

if __name__ == '__main__':
    session = get_db_session()
    zipcodes = {'10003', '12180', '11105', '11215'}
    for z in zipcodes:
        url, name = autocomplete_user_input(z)
        cache = json.dumps(weather_for_url(url, API_KEY))
        session.merge(Location(url, name=name, cache=cache))
    session.commit()
