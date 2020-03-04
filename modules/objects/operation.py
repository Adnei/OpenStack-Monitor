from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String


class Operation(DB_INFO.BASE):
    __tablename__ = 'Operation'
    operationId = Column(Integer, primary_key=True)
    execId = Column(Integer, foreing_key('Execution.execId'))
    type = Column(String)
    meteringDuration = Column(Integer)
    openStackInfoDuration = Column(Integer)
    meteringStart = Column(Integer) #timestamp ???
    meteringFinish = Column(Integer) #timestamp ???
    openStackInfoStart = Column(Integer) #timestamp ???
    openStackInfoFinish = Column(Integer) #timestamp ???

DB_INFO.BASE.metadata.create_all()
