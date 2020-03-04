import time
import logging
import itertools
from modules.openstack_utils import *
from modules.network_meter import *
from modules.objects import db_info
from modules.objects.execution import *
from modules.objects.operation import *
from modules.objects import db_info as DB_INFO
#@TODO: proper indent too long lines

class InstanceLifeCycleMetering:
    autoId = itertools.count()
    def __init__(self, ifaceList=['lo'], execId=None, imageInfo={'imagePath':'Fedora-Cloud-Base-31-1.9.x86_64.qcow2',
                    'imageName':'fedora31',
                    'imageFormat':'qcow2',
                    'imageContainer':'bare'}                         ):
        logging.basicConfig(filename='debug.log', level=logging.DEBUG)
        if execId is None:
            self.id = next(self.autoId)
        else:
            self.id = execId
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
            return round(current - referenceTime)

        if self.instanceImage is None or self.nics is None:
            print("no image or nics") #SHOULD LOG
            return None
        if operationObjectList is None:
            print("Please, provide operationObjectList")
            return None


        execution = Execution(self.id)
        print(execution.id) #DEBUUG
        initSession = DB_INFO.SESSIONMAKER(bind=DB_INFO.ENGINE)
        openSession = initSession()

        openSession.add_all([execution])

        fileList = [iface+'.pcap' for iface in self.ifaceList]
        instance = None
        networkMeter = NetworkMeter(self.ifaceList,outputFileList=fileList)
        elapsedTime = 0
        #instance._info['OS-EXT-STS:vm_state']
        #instance.updated

        for operationObject in operationObjectList:
            print('operation: ', operationObject['operation'])
            startTime = networkMeter.startPacketCapture(fileId=operationObject['operation'].upper() + '_' + str(self.id) + '_')
            time.sleep(1) #tcpdump sync
            if operationObject['operation'].upper() == 'CREATE':
                instance = self.openStackUtils.createInstance('instance',
                                self.instanceImage, operationObject['params']['flavor'], self.nics)
                # operationObject['startedAt'] = startTime
            else:
                if instance.status.upper() in operationObject['requiredStatus']:
                    print('called anonymousFunction!')
                    operationObject['anonymousFunction'](instance)
                else:
                    print('instance\'s current status is not a required status for ', operationObject['targetStatus'])#SHOULD LOG
                    print('You cannot make an instance move from ', instance.status.upper(), ' to ', operationObject['targetStatus'])#SHOULD LOG
                    return
            while instance.status != operationObject['targetStatus']:
                if instance.status.upper() == 'ERROR':
                    print('ERROR') #SHOULD LOG
                    return
                instance.get()
                time.sleep(1)
            finishTime = networkMeter.stopPacketCapture()
            # time.sleep(1) #should sync (?)

        instance.force_delete()
        if not caching:
            self.openStackUtils.deleteImage(self.instanceImage)
            self.instanceName = None
