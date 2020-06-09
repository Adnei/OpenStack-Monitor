from modules.loggers import *
import itertools
import datetime
import dpkt
import os
from modules.objects import db_info as DB_INFO
from modules.objects.os_image import *
from modules.objects.execution import *
from modules.objects.operation import *
from modules.objects.metering import *
from modules.objects.packet_info import *
from modules.objects.service import *
from modules.objects.request_info import *
from service_identifier.lsof_mapper import Lsof_Mapper
import modules.utils as UTILS


#TODO --> Document me :)

class TrafficAnalysis:
    def __init__(self, meteringObj=None, pcapFile=None):
        if meteringObj is None:
            defaultLogger.error('ERROR: No Metering object provided!')
            return None
        if pcapFile is None:
            openSession = DB_INFO.getOpenSession()
            operation = openSession.query(Operation).get(meteringObj.operation_id)
            execution = openSession.query(Execution).get(operation.exec_id)
            osImage = openSession.query(OsImage).get(execution.image_id)
            openSession.close()
            pcapFile = operation.type.upper() + '_' + osImage.image_name + '_' + str(operation.exec_id) + '_' + meteringObj.network_interface + '.pcap'

        lsofFile = 'lsof_' + operation.type.upper() + '_' +  osImage.image_name + '_' + str(operation.exec_id)
        self.lsofMapper = None
        self.servicesMapList = [UTILS.SERVICES_MAP]
        if os.path.isfile(lsofFile):
            self.lsofMapper = Lsof_Mapper(file_path=lsofFile)
            if(self.lsofMapper.is_valid_file):
                self.servicesMapList.append(self.lsofMapper.service_port_mapper)
        self.pcapFile = pcapFile
        self.meteringObj = meteringObj

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


        def savePacket(packetNumber, transportLayerTuple, packetTimestamp, referenceTime, openSession):
            if transportLayerTuple is None:
                return False
            storeList = []
            layers, ip = transportLayerTuple
            transportLayer = ip.data
            packetInfo = PacketInfo(packetNumber=packetNumber)

            packetInfo.src_ip = UTILS.inetToStr(ip.src)
            packetInfo.dst_ip = UTILS.inetToStr(ip.dst)
            packetInfo.size_bytes = ip.len
            packetInfo.sniff_timestamp = str(packetTimestamp)
            packetInfo.time = str(round(packetTimestamp - referenceTime, 6))
            packetInfo.src_port = transportLayer.sport
            packetInfo.dst_port = transportLayer.dport
            #First, tries to find a service corresponding to src_port. If none is found, then tries to find a service corresponding to dst_port.
            matchingService = UTILS.getPortMatchingService(self.servicesMapList, [int(packetInfo.src_port), int(packetInfo.dst_port)])
            if matchingService is not None:
                packetInfo.service_id = matchingService.service_id
            packetInfo.metering_id = self.meteringObj.metering_id
            if 'tcp' in layers:
                packetInfo.tcp_flags = UTILS.tcpFlags(transportLayer.flags)
            packetInfo.layers = layers
            openSession.add(packetInfo)
            #TODO: Store responses
            # Ex.: https://programtalk.com/python-examples/dpkt.http.Response/
            #RequestInfo storing.
            try:
                request = dpkt.http.Request(transportLayer.data)
                layers += ' http'
                packetInfo.layers = layers
                openSession.flush()
                requestInfo = RequestInfo(packetId=packetInfo.packet_id)
                requestInfo.method = request.method
                requestInfo.user_agent = 'NO-USER-AGENT'
                if 'user-agent' in request.headers:
                    requestInfo.user_agent = request.headers['user-agent']
                requestInfo.uri = request.uri
                requestInfo.http_version = request.version
                requestInfo.connection = 'NO-CONNECTION-FLAG'
                if 'connection' in request.headers:
                    requestInfo.connection = request.headers['connection']
                server = UTILS.getPortMatchingService([UTILS.SERVICES_API_MAP], [int(packetInfo.dst_port)])
                if server is not None:
                    requestInfo.server_id = server.service_id
                client = UTILS.getPortMatchingService([UTILS.SERVICES_MAP], [int(packetInfo.src_port)])
                if client is not None:
                    requestInfo.client_id = client.service_id
                openSession.add(requestInfo)
            except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError):
                pass


            return True

        openSession = DB_INFO.getOpenSession()
        packetNumber = 0
        referenceTime = UTILS.getSmallestTimestamp(self.pcapFile)
        ignoredPackets = 0
        with open(self.pcapFile, 'rb') as pcapFile:
            dpktPcap = dpkt.pcap.Reader(pcapFile)
            try:
                for timestamp, packet in dpktPcap:
                    if timestamp < referenceTime:
                        raise ValueError('Reference time is not the smallest one')
                    transportLayerTuple = getTransportLayer(packet)
                    saved = savePacket(packetNumber, transportLayerTuple, timestamp, referenceTime, openSession)
                    packetNumber+= 1
                    if saved == False:
                        ignoredPackets += 1
                        continue
                    openSession.commit()
            except ValueError as error:
                defaultLogger.error(error)
                raise
        openSession.commit()
        openSession.close()

        return ignoredPackets
