import socket
import logging
#import datetime

sqlAlchemyHandler = logging.FileHandler('sqlAlchemyLogs.log')
sqlAlchemyHandler.setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy').addHandler(sqlAlchemyHandler)

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
