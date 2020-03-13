from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey
from sqlalchemy.orm import relationship as Relationship


class PacketInfo(DB_INFO.BASE):
    __tablename__ = 'PacketInfo'
    packet_info_id = Column(Integer, primary_key=True)
    time = Column(String) #timestamp
    src_ip = Column(String)
    dst_ip = Column(String)
    src_port = Column(Integer)
    dst_port = Column(Integer)
    type = Column(String) #Rest or RPC (?)
    size_bytes = Column(Integer) #Float (?)
    service_id = Column(Integer, ForeignKey('Service.service_id', ondelete='cascade'))
    metering_id = Column(Integer, ForeignKey('Metering.metering_id', ondelete='cascade'))

    def __init__(self, serviceName=None):
        if serviceName is not None:
            self.service_name = serviceName


DB_INFO.BASE.metadata.create_all()
