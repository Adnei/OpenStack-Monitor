import logging
import itertools
import calendar
from modules.objects import db_info as DB_INFO
from modules.objects.operation import *
from modules.objects.metering import *

class PacketAnalysis:
    def __init__(self, meteringObj=None, pcapFile=None):
        if meteringObj is None:
            print('ERROR: No Metering object provided!') #SHOULD LOG
            return None
        if pcapFile is None:
            initSession = DB_INFO.SESSIONMAKER(bind=DB_INFO.ENGINE)
            openSession = initSession()
            operation = openSession.query(Operation).get(meteringObj.operation_id)
            pcapFile = operation.type.upper() + '_' + str(operation.exec_id) + '_' +
                        meteringObj.network_interface + '.pcap'

        self.pcapFile = pcapFile
        self.meteringObj = meteringObj
