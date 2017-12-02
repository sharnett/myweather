import sqlalchemy
import json
from wunderground import weather_for_url, autocomplete_user_input
from os.path import dirname, abspath
from database import Location

API_KEY = os.environ.get('WUNDERGROUND_KEY', 'development')
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.db'

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
