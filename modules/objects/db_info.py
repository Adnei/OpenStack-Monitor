from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


ENGINE = create_engine('sqlite:///network_metering_experiment.db', echo=False)
BASE = declarative_base(bind=ENGINE)
SESSIONMAKER = sessionmaker

sqlAlchemyHandler = logging.FileHandler('sqlAlchemyLogs.log')
sqlAlchemyHandler.setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy.engine').addHandler(sqlAlchemyHandler)
