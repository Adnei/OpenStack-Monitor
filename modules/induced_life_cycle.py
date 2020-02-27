import time
import logging
from openstack_utils import *
from network_meter import *


class InstanceLifeCycleMetering:
    def __init__(self, ifaceList=['lo']):
        logging.basicConfig(filename='debug.log', level=logging.DEBUG)
        self.ifaceList = ifaceList
        self.openStackUtils = OpenStackUtils() #use default authInfo
        self.instance = None
        self.instanceImage = None
        self.nics = None

    def prepareLifeCycleScenario(self):
        #create image and network
        self.instanceImage = self.openStackUtils.createImage()
        self.nics = self.openStackUtils.networkSetup()

    def startInducedLifeCycle(self, stateList=['create','suspend','resume','stop','shelve']):
        if self.instanceImage == None or self.nics == None:
            return None

        fileList = ['create_'+iface+'.pcap' for iface in argv] #['create_enp3s0.pcap','create_lo.pcap']
        networkMeter = NetworkMeter(self.ifaceList,outputFileList=fileList)
        networkMeter.startPacketCapture()

        instance = self.openStackUtils.createInstance('instance', self.instanceImage, 'm1.small', self.nics)

        while instance.status == 'BUILD':
            instance.get()
            time.sleep(1)
        if instance.status != 'ACTIVE':
            print("ERROR!!!!!!")
            print(instance.status)
        networkMeter.stopPacketCapture()
