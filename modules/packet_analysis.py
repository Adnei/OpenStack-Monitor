import logging
import itertools
import datetime
import pyshark as PyShark
from modules.objects import db_info as DB_INFO
from modules.objects.operation import *
from modules.objects.metering import *
from modules.objects.packet_info import *


class TrafficAnalysis:
    def __init__(self, meteringObj=None, pcapFile=None):
        def getServices():
            initSession = DB_INFO.SESSIONMAKER(bind=DB_INFO.ENGINE)
            openSession = initSession()
            services = openSession.query(Service).all()
            openSession.close()
            return services

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
        self.services = getServices()

    def printPyShark(self):
        captureFile = PyShark.FileCapture(self.pcapFile)
        print(captureFile[0])

    def runAnalysis(self):
        def buildPacketInfo(packet, referenceTime):
            packetInfo = PacketInfo(packetNumber=int(packet.number))
            packetInfo.sniff_timestamp = packet.sniff_timestamp
            packetInfo.time = (packet.sniff_time - referenceTime).total_seconds()
            #Try Catch
            packetInfo.src_ip = packet.ip.src
            packetInfo.dst_ip = packet.ip.dst
            packetInfo.src_port = packet[packet.transport_layer].srcport
            packetInfo.dst_port = packet[packet.transport_layer].dstport
            layers = ''
            for layer in packet.layers:
                if(layer.layer_name not in layers):
                    layers += layer.layer_name + ' '
            packetInfo.layers = layers
            packetInfo.size_bytes = packet.length
            #service id
            packetInfo.metering_id = self.meteringObj.metering_id

            return packetInfo

        def buildApiInfo(packet, referenceTime):
            print('NOT YET')

        capFile = PyShark.FileCapture(self.pcapFile)
        initSession = DB_INFO.SESSIONMAKER(bind=DB_INFO.ENGINE)
        openSession = initSession()
        for packet in capFile:
            packetInfo = buildPacketInfo(packet, capFile[0].sniff_time)
            openSession.add(packetInfo)
        openSession.commit()
        openSession.close()
