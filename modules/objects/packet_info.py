from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey
from sqlalchemy.orm import relationship as Relationship


class PacketInfo(DB_INFO.BASE):
    __tablename__ = 'PacketInfo'
    packet_number = Column(Integer, primary_key=True)
    sniff_timestamp = Column(String) #timestamp
    time = Column(String) #Absolute time between the current packet and the first packet (seconds)
    src_ip = Column(String)
    dst_ip = Column(String)
    src_port = Column(Integer)
    dst_port = Column(Integer)
    #layers = Column(String) #Rest or RPC (?)
    #TODO: Identify AMQP packet
    size_bytes = Column(Integer) #Float (?)
    service_id = Column(Integer, ForeignKey('Service.service_id', ondelete='cascade'))
    metering_id = Column(Integer, ForeignKey('Metering.metering_id', ondelete='cascade'))

    def __init__(self, serviceName=None, packetNumber=None):
        if serviceName is not None:
            self.service_name = serviceName
        if packetNumber is not None:
            self.packet_number= packetNumber


DB_INFO.BASE.metadata.create_all()
