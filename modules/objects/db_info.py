# import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# logging.basicConfig()
# sqlAlchemyHandler = logging.FileHandler('sqlAlchemyLogs.log')
# sqlAlchemyHandler.setLevel(logging.DEBUG)
# logging.getLogger('sqlalchemy').addHandler(sqlAlchemyHandler)
# logging.getLogger('sqlalchemy').propagate = False

ENGINE = create_engine('sqlite:///network_metering_experiment.db', echo="debug")
BASE = declarative_base(bind=ENGINE)
SESSIONMAKER = sessionmaker
