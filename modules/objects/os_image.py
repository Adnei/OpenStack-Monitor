from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey
from sqlalchemy.orm import relationship as Relationship

class OsImage(DB_INFO.BASE):
    __tablename__ = 'OsImage'
    image_id = Column(Integer, primary_key=True)
    file_path = Column(String)
    image_name = Column(String)
    image_format = Column(String)
    image_container = Column(String)
    username = Column(String)
    executions = Relationship('Execution')


    def __init__(self, serviceName=None):
        if serviceName is not None:
            self.service_name = serviceName
