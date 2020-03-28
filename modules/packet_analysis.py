import logging
import itertools
import calendar
import pyshark as PyShark
from modules.objects import db_info as DB_INFO
from modules.objects.operation import *
from modules.objects.metering import *


class TrafficAnalysis:
    def __init__(self, meteringObj=None, pcapFile=None):
        if meteringObj is None:
            print('ERROR: No Metering object provided!') #SHOULD LOG
            return None
        if pcapFile is None:
            initSession = DB_INFO.SESSIONMAKER(bind=DB_INFO.ENGINE)
            openSession = initSession()
            operation = openSession.query(Operation).get(meteringObj.operation_id)
            openSession.close()
            pcapFile = operation.type.upper() + '_' + str(operation.exec_id) + '_' + meteringObj.network_interface + '.pcap'

        self.pcapFile = pcapFile
        self.meteringObj = meteringObj

    def printPyShark(self):
        captureFile = PyShark.FileCapture(self.pcapFile)
        print(captureFile[0])
