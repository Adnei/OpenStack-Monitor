from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey
from sqlalchemy.orm import relationship as Relationship


class Execution(DB_INFO.BASE):
    __tablename__ = 'Execution'
    exec_id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('OsImage.image_id', ondelete='cascade'))
    operations = Relationship('Operation')

    def __init__(self, imageId=None):
        if imageId is not None:
            self.image_id = imageId
