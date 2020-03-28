 #API Calls will no longer exists
from modules.objects import db_info as DB_INFO
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, ForeignKey
from sqlalchemy.orm import relationship as Relationship


class Service(DB_INFO.BASE):
    __tablename__ = 'Service'
    service_id = Column(Integer, primary_key=True)
    service_name = Column(String)
    api_info_list = Relationship('ApiInfo')
    packet_info_list = Relationship('PacketInfo')


    def __init__(self, serviceName=None):
        if serviceName is not None:
            self.service_name = serviceName


DB_INFO.BASE.metadata.create_all()

defaultServices = [ Service(name=service) for service in [  'nova',
                                                            'keystone',
                                                            'swift',
                                                            'glance',
                                                            'cinder',
                                                            'neutron' ]]
initSession = DB_INFO.SESSIONMAKER(bind=DB_INFO.ENGINE)
openSession = initSession()
openSession.commit_all(defaultServices)
openSession.close()
