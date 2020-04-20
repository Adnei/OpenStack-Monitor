from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey
from sqlalchemy.orm import relationship as Relationship

class RequestInfo(DB_INFO.BASE):
    __tablename__ = 'RequestInfo'
    request_info_id = Column(Integer, primary_key=True)
    method = Column(String)
    user_agent = Column(String)
    packet_id = Column(Integer, ForeignKey('PacketInfo.packet_id', ondelete='cascade'))
    #OpenStack's services may act as Client - Server between themselves
    #Incase we don't know the port owner (service) then Client/Service will be None
    server_id = Column(Integer, ForeignKey('Service.service_id', ondelete='cascade'))
    client_id = Column(Integer, ForeignKey('Service.service_id', ondelete='cascade'))

    def __init__(self, packetId=None):
        if packetId is not None:
            self.packet_id = packetId


DB_INFO.BASE.metadata.create_all()
