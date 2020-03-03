import time
import logging
import itertools
from modules.openstack_utils import *
from modules.network_meter import *


#@TODO: proper indent too long lines

class InstanceLifeCycleMetering:
    autoId = itertools.count()
    def __init__(self, ifaceList=['lo'], imageInfo={'imagePath':'Fedora-Cloud-Base-31-1.9.x86_64.qcow2',
                    'imageName':'fedora31',
                    'imageFormat':'qcow2',
                    'imageContainer':'bare'}                         ):
        logging.basicConfig(filename='debug.log', level=logging.DEBUG)
        self.ifaceList = ifaceList
        self.openStackUtils = OpenStackUtils() #use default authInfo
        self.instanceImage, self.nics = self.prepareLifeCycleScenario(imageInfo)
        self.id = next(self.autoId)

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
        time.sleep(1) #tcpdump sync

        #instance._info['OS-EXT-STS:vm_state']
        #instance.updated
        # TODO: Integrate vm_state_report
        # Separete by .pcap // keep it all in one .pcap

        for operationObject in operationObjectList:
            print('operation: ', operationObject['operation'])
            if operationObject['operation'].upper() == 'CREATE':
                instance = self.openStackUtils.createInstance('instance',
                                self.instanceImage, operationObject['params']['flavor'], self.nics)
                operationObject['startedAt'] = startTime
            else:
                if instance.status.upper() in operationObject['requiredStatus']:
                    print('called anonymousFunction!')
                    operationObject['started'] = time.time()
                    operationObject['anonymousFunction'](instance)
                else:
                    return #SHOULD LOG
            while instance.status != operationObject['targetStatus']:
                if instance.status.upper() == 'ERROR':
                    print('ERROR') #SHOULD LOG
                    return
                instance.get()
                time.sleep(1)
            operationObject['finishedAt'] = time.time()
            operationObject['elapsedSecs'] = elapsedTime(operationObject['finishedAt'])
        finishTime = networkMeter.stopPacketCapture()

        instance.force_delete()
        if not caching:
            self.openStackUtils.deleteImage(self.instanceImage)
            self.instanceName = None
