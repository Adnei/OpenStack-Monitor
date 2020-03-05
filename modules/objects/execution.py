from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String


class Execution(DB_INFO.BASE):
    __tablename__ = 'Execution'
    execId = Column(Integer, primary_key=True)

DB_INFO.BASE.metadata.create_all()
