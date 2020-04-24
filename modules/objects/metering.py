from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey
from sqlalchemy.orm import relationship as Relationship


class Metering(DB_INFO.BASE):
    __tablename__ = 'Metering'
    metering_id = Column(Integer, primary_key=True)
    network_interface = Column(String, nullable=False)
    operation_id = Column(Integer, ForeignKey('Operation.operation_id', ondelete='cascade'))
    packet_info_list = Relationship('PacketInfo')


    def __init__(self, parentId=None, iface=None):
        if parentId is not None:
            self.operation_id = parentId
        if iface is not None:
            self.network_interface = iface
