from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


ENGINE = create_engine('sqlite:///teste.db', echo=True)
BASE = declarative_base(bind=ENGINE)
SESSIONMAKER = sessionmaker
