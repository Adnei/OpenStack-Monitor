import time
import logging
from modules.openstack_utils import *
from modules.network_meter import *


#@TODO: proper indent too long lines

class InstanceLifeCycleMetering:
    def __init__(self, ifaceList=['lo'], imageInfo={'flavor':'m1.small',
                    'imagePath':'Fedora-Cloud-Base-31-1.9.x86_64.qcow2',
                    'imageName':'fedora31',
                    'imageFormat':'qcow2',
                    'imageContainer':'bare'}                         ):
        logging.basicConfig(filename='debug.log', level=logging.DEBUG)
        self.ifaceList = ifaceList
        self.openStackUtils = OpenStackUtils() #use default authInfo
        self.instanceImage, self.nics = self.prepareLifeCycleScenario(imageInfo)

    def prepareLifeCycleScenario(self, imageInfo):
        #create image and network
        self.instanceImage = self.openStackUtils.createImage(imageInfo)
        self.nics = self.openStackUtils.networkSetup()

        gotInstance = self.openStackUtils.getInstanceByName('fedora31')
        print("got instance ->", gotInstance)

        return (self.instanceImage, self.nics)

    def startInducedLifeCycle(self, stateList=['create','suspend','resume',
                                          'stop','shelve'], caching=False):
        if self.instanceImage == None or self.nics == None:
            return None

        #['create_enp3s0.pcap','create_lo.pcap']
        # @TODO Parameterize file names
        fileList = ['create_'+iface+'.pcap' for iface in self.ifaceList]
        networkMeter = NetworkMeter(self.ifaceList,outputFileList=fileList)
        startTime = networkMeter.startPacketCapture()

        instance = self.openStackUtils.createInstance('instance',
                        self.instanceImage, 'm1.small', self.nics)

        while instance.status == 'BUILD':
            instance.get()
            time.sleep(1)
        if instance.status != 'ACTIVE':
            print("ERROR!!!!!!")
            print(instance.status)
        stopTime = networkMeter.stopPacketCapture()
        if(not caching):
            #try catch
            self.openStackUtils.deleteImage(self.glanceImage)
            self.glanceImage = None
        print("started at -> ", startTime)
        print("stopped at -> ", stopTime)
