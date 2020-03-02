import time
import logging
from modules.openstack_utils import *
from modules.network_meter import *


#@TODO: proper indent too long lines

class InstanceLifeCycleMetering:
    def __init__(self, ifaceList=['lo'], imageInfo={'imagePath':'Fedora-Cloud-Base-31-1.9.x86_64.qcow2',
                    'imageName':'fedora31',
                    'imageFormat':'qcow2',
                    'imageContainer':'bare'}                         ):
        logging.basicConfig(filename='debug.log', level=logging.DEBUG)
        self.ifaceList = ifaceList
        self.openStackUtils = OpenStackUtils() #use default authInfo
        self.instanceImage, self.nics = self.prepareLifeCycleScenario(imageInfo)

    def prepareLifeCycleScenario(self, imageInfo):
        #create image and network
        cachedImage = self.openStackUtils.getImageByName('fedora31')
        if cachedImage is None:
            print('Image is not being cached!') #Should Log
        self.instanceImage = cachedImage if cachedImage is not None else self.openStackUtils.createImage(imageInfo)
        self.nics = self.openStackUtils.networkSetup()

        return (self.instanceImage, self.nics)

    def startInducedLifeCycle(self, operationObjectList, caching=False):
        def elapsedTime(referenceTime, current=time.time()):
            return
        return round(current - referenceTime)

        if self.instanceImage is None or self.nics is None:
            print("no image or nics") #SHOULD LOG
            return None
        if operationObjectList is None:
            print("Please, provide operationObjectList")
            return None

        #['create_enp3s0.pcap','create_lo.pcap']
        # @TODO Parameterize file names
        fileList = [iface+'.pcap' for iface in self.ifaceList]
        networkMeter = NetworkMeter(self.ifaceList,outputFileList=fileList)
        startTime = networkMeter.startPacketCapture()
        instance = None

        for operationObject in operationObjectList:
            print('operaton: ', operationObject['operaton'])
            if operationObject['operation'].upper() == 'CREATE':
                instance = self.openStackUtils.createInstance('instance',
                                self.instanceImage, operationObject['params']['flavor'], self.nics)
                operationObject['startedAt'] = startTime
            else:
                print('called anonymousFunction!')
                operationObject['anonymousFunction'](instance)
            while instance.status != operationObject['targetState'] or instance.status != 'ERROR':
                instance.get()
                time.sleep(1)
            operationObject['finishedAt'] = time.time()
        finishTime = networkMeter.stopPacketCapture()
