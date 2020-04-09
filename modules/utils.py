import socket
from modules.objects import db_info as DB_INFO
from modules.objects.service import *


SERVICES_MAP = {
    'nova': set([5900, 6080, 6081, 6082, 8773, 8774, 8775] + list(range(5900, 5999))),
    'keystone': {5000, 35357},
    'swift': {873, 6000, 6001, 6002, 8080},
    'glance': {9191, 9292},
    'cinder': {3260, 8776},
    'neutron': {9696}
}

SERVICES_API_MAP = {
        'nova': {8774},
        'keystone': {5000, 35357},
        'swift': {8080},
        'glance': {9292},
        'cinder': {8776},
        'neutron': {9696},
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


def invertDict(dict):
        resultDict = {}
        for key in dict:
            for value in dict[key]:
                resultDict[value] = key
        return resultDict

def getServices():
    openSession = DB_INFO.getOpenSession()
    services = openSession.query(Service).all()
    openSession.close()
    return services

def getPortMatchingService(services, servicesMap, matchPort):
    portServicesMap = invertDict(servicesMap)
    if(matchPort not in portServicesMap):
        return None
    serviceName = portServicesMap[matchPort]
    resultService = [service for service in services if service.service_name == serviceName][0]
    return resultService
