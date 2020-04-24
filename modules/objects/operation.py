from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey
from sqlalchemy.orm import relationship as Relationship


class Operation(DB_INFO.BASE):
    __tablename__ = 'Operation'
    operation_id = Column(Integer, primary_key=True)
    exec_id = Column(Integer, ForeignKey('Execution.exec_id', ondelete='cascade'))
    type = Column(String)
    metering_list = Relationship('Metering')
    metering_start = Column(Integer) #timestamp ??? Float
    metering_finish = Column(Integer) #timestamp ??? Float
    openstack_info_start = Column(Integer) #timestamp ??? Float
    openstack_info_finish = Column(Integer) #timestamp ??? Float

    #Columns calculated from Metering and OpenStackInfo finish and start
    metering_duration = Column(Integer)
    openstack_info_duration = Column(Integer)

    def __init__(self, parentId=None):
        if parentId is not None:
            self.exec_id = parentId
