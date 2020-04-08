import logging
import itertools
import datetime
import pyshark as PyShark
from modules.objects import db_info as DB_INFO
from modules.objects.operation import *
from modules.objects.metering import *
from modules.objects.packet_info import *
from modules.objects.service import *
from modules.utils import inetToStr


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
        def buildPacketInfo(packetNumber, packet, packetTimestamp, referenceTime):
            ignored = False
            packetInfo = PacketInfo(packetNumber=packetNumber)
            packetInfo.sniff_timestamp = packetTimestamp
            packetInfo.time = round(packetTimestamp - referenceTime, 6)

            ethLayer = dpkt.ethernet.Ethernet(packet)
            # Make sure the Ethernet frame contains an IP packet
            if not isinstance(ethLayer.data, dpkt.ip.IP):
                print ('Non IP Packet type not supported --> ', ethLayer.data.__class__.__name__, '\n')
                ignored = True
                return (ignored, None)
            ip = ethLayer.data
            layers = ''
            if ip.p == dpkt.ip.IP_PROTO_TCP:
                layers += 'tcp '
                TCP = ip.data
                srcport = TCP.sport
                dstport = TCP.dport
            elif ip.p == dpkt.ip.IP_PROTO_UDP:
                UDP = ip.data
                layers += 'udp '
                packetInfo.src_port = UDP.sport
                packetInfo.dst_port = UDP.dport
            else:
                print('Transport layer protocol not supported. Only TCP and UDP are supported')
                ignored = True
                return (ignored, None)

            packetInfo.src_ip = inetToStr(ip.src)
            packetInfo.dst_ip = inetToStr(ip.dst)
            print('packet len --> ', ip.length)
            packetInfo.size_bytes = ip.length
            #TODO: mapping service and getting service id
            packetInfo.metering_id = self.meteringObj.metering_id

            return (ignored, packetInfo)

        def buildApiInfo(packet, referenceTime):
            print('NOT YET')

        initSession = DB_INFO.SESSIONMAKER(bind=DB_INFO.ENGINE)
        openSession = initSession()
        packetNumber = 0
        referenceTime = 0
        ignoredPackets = 0
        pcapFile = open(self.pcapFile, 'rb')
        dpktPcap = dpkt.pcap.Reader(pcapFile)
        for timestamp, packet in dpktPcap:
            print('PACKET --> ', packetNumber)
            if packetNumber == 0:
                referenceTime = timestamp
            else:
                if timestamp < referenceTime:
                    print('ERROR!!! Packets are not sorted by timestamp')
                    break
            ignored, packetInfo = buildPacketInfo(packetNumber, packet, packetTimestamp, referenceTime)
            if ignored:
                ignoredPackets += 1
                continue
            openSession.add(packetInfo)
            openSession.commit()
            packetNumber+= 1
        # openSession.commit()
        openSession.close()
