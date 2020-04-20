# import logging
from modules.loggers import *
import itertools
import datetime
import pyshark as PyShark
from modules.objects import db_info as DB_INFO
from modules.objects.operation import *
from modules.objects.metering import *
from modules.objects.packet_info import *
from modules.objects.service import *
import dpkt
import modules.utils as UTILS

class TrafficAnalysis:
    def __init__(self, meteringObj=None, pcapFile=None):
        if meteringObj is None:
            defaultLogger.error('ERROR: No Metering object provided!')
            return None
        if pcapFile is None:
            openSession = DB_INFO.getOpenSession()
            operation = openSession.query(Operation).get(meteringObj.operation_id)
            openSession.close()
            pcapFile = operation.type.upper() + '_' + str(operation.exec_id) + '_' + meteringObj.network_interface + '.pcap'

        self.pcapFile = pcapFile
        self.meteringObj = meteringObj
        self.services = UTILS.getServices()

    def printPyShark(self):
        captureFile = PyShark.FileCapture(self.pcapFile)
        print(captureFile[0])

    def runAnalysis(self):
        def getTransportLayer(packet):
            ethLayer = dpkt.ethernet.Ethernet(packet)
            # Make sure the Ethernet frame contains an IP packet
            if not isinstance(ethLayer.data, dpkt.ip.IP):
                defaultLogger.critical('Non IP Packet type not supported: %s \n', ethLayer.data.__class__.__name__)
                return None
            ip = ethLayer.data
            #currently not supporting ARP
            #TODO Should support ARP
            if ip.p == dpkt.ip.IP_PROTO_TCP:
                layerName = 'tcp'
            elif ip.p == dpkt.ip.IP_PROTO_UDP:
                layerName = 'udp'
            else:
                defaultLogger.critical('Transport layer protocol not supported. Only TCP and UDP are supported')
                return None
            return (layerName, ip)


        def savePacket(packetNumber, ipLayer, transportLayerTuple, referenceTime, openSession):
            if transportLayerTuple is None:
                return None
            storeList = []
            layers, ip = transportLayerTuple
            transportLayer = ip.data
            packetInfo = PacketInfo(packetNumber=packetNumber)

            packetInfo.src_ip = UTILS.inetToStr(ip.src)
            packetInfo.dst_ip = UTILS.inetToStr(ip.dst)
            packetInfo.size_bytes = ip.len
            packetInfo.sniff_timestamp = packetTimestamp
            packetInfo.time = round(packetTimestamp - referenceTime, 6)
            packetInfo.src_port = transportLayer.sport
            packetInfo.dst_port = transportLayer.dport
            matchingService = UTILS.getPortMatchingService(self.services, UTILS.SERVICES_MAP, int(packetInfo.src_port))
            if matchingService is not None:
                packetInfo.service_id = matchingService.service_id
            packetInfo.metering_id = self.meteringObj.metering_id
            if 'tcp' in layers:
                #FIXME Not sure if passing dpkt as parameter is the best option
                #Should have a look about which is the best approach: importing dpk (inside utils module) or passing by parameter
                packetInfo.tcp_flags = UTILS.tcpFlags(transportLayer.flags, dpkt)
            packetInfo.layers = layers
            openSession.add(packetInfo)

            try:
                request = dpkt.http.Request(transportLayer.data)
                layers += ' http'
                packetInfo.layers = layers
                openSession.flush()
                requestInfo = RequestInfo(packetId=packetInfo.packet_id)
                requestInfo.method = request.method
                requestInfo.user_agent = request.headers['user-agent']

                server = UTILS.getPortMatchingService(self.services, UTILS.SERVICES_MAP, int(packetInfo.dst_port))
                if server is not None:
                    requestInfo.server_id = server.service_id
                client = UTILS.getPortMatchingService(self.services, UTILS.SERVICES_MAP, int(packetInfo.src_port))
                if client is not None:
                    requestInfo.client_id = client.service_id

                defaultLogger.info('Saved a request info for packet: ', packetInfo.packet_id)
            except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError):
                pass


            return True

        openSession = DB_INFO.getOpenSession()
        packetNumber = 0
        referenceTime = 0
        ignoredPackets = 0
        with open(self.pcapFile, 'rb') as pcapFile:
            dpktPcap = dpkt.pcap.Reader(pcapFile)
            for timestamp, packet in dpktPcap:
                if packetNumber == 0:
                    referenceTime = timestamp
                else: #It's not necessary, but just to make sure it's sorted by timestamp
                    if timestamp < referenceTime:
                        defaultLogger.error('ERROR!!! Packets are not sorted by timestamp')
                        break

                transportLayerTuple = getTransportLayer(packet)
                saved = savePacket(packetNumber, transportLayerTuple, timestamp, referenceTime, openSession)
                if saved == False:
                    ignoredPackets += 1
                    continue
                # openSession.add_all(packetInfo)
                openSession.commit()
                packetNumber+= 1
        openSession.commit()
        openSession.close()

        return ignoredPackets





#         for ts, pkt in dpktPcap:
# ...     _ts = ts
# ...     packet = pkt
# ...     ethLayer = dpkt.ethernet.Ethernet(pkt)
# ...     if not isinstance(ethLayer.data, dpkt.ip.IP):
# ...             continue
# ...     ip = ethLayer.data
# ...     if ip.p == dpkt.ip.IP_PROTO_TCP:
# ...             TCP = ip.data
# ...             if TCP.dport == 9292 and len(TCP.data) > 0:
# ...                     http = dpkt.http.Request(TCP.data)
# ...                     break
