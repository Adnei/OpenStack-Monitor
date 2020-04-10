from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey
from sqlalchemy.orm import relationship as Relationship


class ApiInfo(DB_INFO.BASE):
    __tablename__ = 'ApiInfo'
    packet_info_id = Column(Integer, primary_key=True)
    src_port = Column(Integer)
    dst_port = Column(Integer)
    called = Column(Integer, ForeignKey('Service.service_id', ondelete='cascade'))
    caller = Column(Integer, ForeignKey('Service.service_id', ondelete='cascade'))
    method = Column(String)
    size_bytes = Column(Integer)
    metering_id = Column(Integer, ForeignKey('Metering.metering_id', ondelete='cascade'))

    def __init__(self, serviceName=None):
        if serviceName is not None:
            self.service_name = serviceName


DB_INFO.BASE.metadata.create_all()
