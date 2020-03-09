from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey
from sqlalchemy.orm import relationship as Relationship


class Metering(DB_INFO.BASE):
    __tablename__ = 'Metering'
    metering_id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey('Operation.operation_id', ondelete='cascade'))
    operation = Relationship('Operation', back_populates='metering')

    def __init__(self, parentId=None):
        if parentId is not None:
            self.operation_id = parentId


DB_INFO.BASE.metadata.create_all()
