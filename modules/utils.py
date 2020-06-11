import socket
import dpkt
from modules.loggers import *
from modules.objects import db_info as DB_INFO
from modules.objects.service import *
from modules.objects.os_image import *

#https://docs.openstack.org/mitaka/config-reference/firewalls-default-ports.html
#https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/10/html/firewall_rules_for_red_hat_openstack_platform/index

SERVICES_MAP = {
    'nova': set([5900, 6080, 6081, 6082, 8773, 8774, 8775] + list(range(5900, 5999))),
    'keystone': {5000, 35357},
    'swift': {873, 6000, 6001, 6002, 8080},
    'glance': {9191, 9292},
    'cinder': {3260, 8776},
    'neutron': {9696},
    'heat': {8004}
}


#@IMPORTANT - These API ports won't match for EC2 integration and 'over SSL' communication
# These API ports are the most basic ones
# This is not a FIXME because it's out of the scope of the experiments
SERVICES_API_MAP = {
        'nova': {8774, 8775}, #8775 nova-api metadata
        'keystone': {5000, 35357},
        'swift': {8080},
        'glance': {9292},
        'cinder': {8776},
        'neutron': {9696},
        'heat': {8004}
    }

#Source: https://dpkt.readthedocs.io/en/latest/_modules/examples/print_packets.html
def inetToStr(inet):
    """Convert inet object to a string

        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)


# Source: https://blog.bramp.net/post/2010/01/10/follow-http-stream-with-decompression/
def tcpFlags(flags):
    ret = ''
    if flags & dpkt.tcp.TH_FIN:
        ret = ret + 'F'
    if flags & dpkt.tcp.TH_SYN:
        ret = ret + 'S'
    if flags & dpkt.tcp.TH_RST:
        ret = ret + 'R'
    if flags & dpkt.tcp.TH_PUSH:
        ret = ret + 'P'
    if flags & dpkt.tcp.TH_ACK:
        ret = ret + 'A'
    if flags & dpkt.tcp.TH_URG:
        ret = ret + 'U'
    if flags & dpkt.tcp.TH_ECE:
        ret = ret + 'E'
    if flags & dpkt.tcp.TH_CWR:
        ret = ret + 'C'

    return ret


def invertDict(dict):
        resultDict = {}
        for key in dict:
            for value in dict[key]:
                resultDict[value] = key
        return resultDict

#
# TODO Maybe create something like a DAO
#
def getServices():
    openSession = DB_INFO.getOpenSession()
    services = openSession.query(Service).all()
    openSession.close()
    return services

def getServiceByName(serviceName):
    openSession = DB_INFO.getOpenSession()
    service = openSession.query(Service).filter_by(service_name=serviceName).first()
    openSession.close()
    return service

def createServicesFromMapper(servicePortMapper):
    services = [Service(serviceName=service) for service in servicePortMapper if getServiceByName(service) is None]
    openSession = DB_INFO.getOpenSession()
    openSession.add_all(services)
    openSession.commit()
    openSession.close()


def getPortMatchingService(servicesMapList, matchPortList):
    """
        @ATTENTION:
            This method is O(n^2) (in worst case), depending on the size of servicesMapList and matchPortsList


        Gets a service according to its port.
        If more than one port is provided, then the first match will be returned.
        If no matches, then returns None.

        Parameters:
                    servicesMapList: A list of maps holding all the services and its ports. see SERVICES_MAP, for example
                    matchPortList (array of int): list of ports to be matched against the services map
        Returns:
                    <Service>, the first service found corresponding to a port
                    None, if there's no corresponding service for the provided matchPortList

    """

    portMapList = [invertDict(serviceMap) for serviceMap in servicesMapList]
    for matchPort in matchPortList:
        for portMap in portMapList:
            if(matchPort in portMap):
                serviceName = portMap[matchPort]
                return getServiceByName(serviceName)
    return None

def createOsImage(imageInfoList):
    openSession = DB_INFO.getOpenSession(expire_on_commit=False)
    defaultImageFormat = 'qcow2'
    defaultImageContainer = 'bare'
    osImageList = []
    for imageInfo in imageInfoList:
        if 'imagePath' not in imageInfo or 'imageName' not in imageInfo:
            defaultLogger.error('ERROR: Need image file path and image name')
            # openSession.rollback()
            openSession.close()
            return None

        osImage = OsImage()
        osImage.file_path = imageInfo['imagePath']
        osImage.image_name = imageInfo['imageName']
        osImage.image_format = defaultImageFormat
        if 'imageFormat' in imageInfo:
            osImage.image_format = imageInfo['imageFormat']
        osImage.image_container = defaultImageContainer
        if 'imageContainer' in imageInfo:
            osImage.image_container = imageInfo['imageContainer']
        openSession.add(osImage)
        osImageList.append(osImage)

    openSession.commit()
    openSession.close()
    return osImageList

def getSmallestTimestamp(pcapPath):
    count = 0
    smallest = 0
    with open(pcapPath, 'rb') as pcapFile:
        dpktPcap = dpkt.pcap.Reader(pcapFile)
        for timestamp, __ in dpktPcap:
            if count == 0 or timestamp < smallest:
                smallest = timestamp
            count += 1
    return smallest
