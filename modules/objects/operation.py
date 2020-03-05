from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey


class Operation(DB_INFO.BASE):
    __tablename__ = 'Operation'
    operationId = Column(Integer, primary_key=True)
    execId = Column(Integer, ForeignKey('Execution.execId'))
    type = Column(String)
    meteringStart = Column(Integer) #timestamp ???
    meteringFinish = Column(Integer) #timestamp ???
    openStackInfoStart = Column(Integer) #timestamp ???
    openStackInfoFinish = Column(Integer) #timestamp ???
    meteringDuration = Column(Integer)
    openStackInfoDuration = Column(Integer)

DB_INFO.BASE.metadata.create_all()
