from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String
from sqlalchemy.orm import relationship as Relationship


class Execution(DB_INFO.BASE):
    __tablename__ = 'Execution'
    exec_id = Column(Integer, primary_key=True)
    operations = Relationship('Operation')

DB_INFO.BASE.metadata.create_all()
