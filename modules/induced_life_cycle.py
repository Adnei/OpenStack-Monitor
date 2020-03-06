import time
import logging
import itertools
import calendar
from datetime import datetime
from modules.openstack_utils import *
from modules.network_meter import *
from modules.objects import db_info
from modules.objects.execution import *
from modules.objects.operation import *
from modules.objects import db_info as DB_INFO
#@TODO: proper indent too long lines

class InstanceLifeCycleMetering:
    autoId = itertools.count()
    def __init__(self, ifaceList=['lo'], imageInfo={'imagePath':'Fedora-Cloud-Base-31-1.9.x86_64.qcow2',
                    'imageName':'fedora31',
                    'imageFormat':'qcow2',
                    'imageContainer':'bare'}                         ):
        logging.basicConfig(filename='debug.log', level=logging.DEBUG)
        self.imageInfo = imageInfo
        self.ifaceList = ifaceList
        self.openStackUtils = OpenStackUtils() #use default authInfo
        self.instanceImage, self.nics = self.prepareLifeCycleScenario(imageInfo)


    def prepareLifeCycleScenario(self, imageInfo):
        #create image and network
        cachedImage = self.openStackUtils.getImageByName(imageInfo['imageName'])
        if cachedImage is None:
            print('Image is not being cached!') #Should Log
        self.instanceImage = cachedImage if cachedImage is not None else self.openStackUtils.createImage(imageInfo)
        self.nics = self.openStackUtils.networkSetup()

        return (self.instanceImage, self.nics)

    def startInducedLifeCycle(self, operationObjectList, caching=False):
        if self.instanceImage is None or self.nics is None:
            self.instanceImage, self.nics = self.prepareLifeCycleScenario(self.imageInfo)
        if operationObjectList is None:
            print("Please, provide operationObjectList")
            return None

        UTC_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
        START_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
        execution = Execution()
        initSession = DB_INFO.SESSIONMAKER(bind=DB_INFO.ENGINE)
        openSession = initSession()

        openSession.add(execution)
        openSession.commit()#SQLAlchemy handles the ID auto increment

        fileList = [iface+'.pcap' for iface in self.ifaceList]
        instanceServer = None
        networkMeter = NetworkMeter(self.ifaceList,outputFileList=fileList)
        operationList = []
        #Other infos about instanceServer -> instanceServer._info['OS-EXT-STS:vm_state']

        #
        # INDUCED LIFE CYCLE LOGIC
        #

        for operationObject in operationObjectList:
            print('operation: ', operationObject['operation'])
            operation = Operation()
            operation.execId = execution.execId
            operation.type = operationObject['operation'].upper()
            startTimestamp = networkMeter.startPacketCapture(fileId=operationObject['operation'].upper() + '_' + str(execution.execId) + '_')
            operation.meteringStart = datetime.utcfromtimestamp(startTimestamp).timestamp() # get utc format instead of time since epoch
            time.sleep(1) #tcpdump sync
            if operationObject['operation'].upper() == 'CREATE':
                instanceServer = self.openStackUtils.createInstance('instanceServer',
                                self.instanceImage, operationObject['params']['flavor'], self.nics)
            else:
                if instanceServer.status.upper() in operationObject['requiredStatus']:
                    print('called anonymousFunction!')
                    operationObject['anonymousFunction'](instanceServer)
                else:
                    print('instanceServer\'s current status is not a required status for ', operationObject['targetStatus'])#SHOULD LOG
                    print('You cannot make a server status move from ', instanceServer.status.upper(), ' to ', operationObject['targetStatus'])#SHOULD LOG
                    networkMeter.stopPacketCapture()
                    return
            while instanceServer.status != operationObject['targetStatus']:
                if instanceServer.status.upper() == 'ERROR':
                    print('Server status: ERROR') #SHOULD LOG
                    print('Aborting')
                    networkMeter.stopPacketCapture()
                    return
                instanceServer.get()
                time.sleep(1)
            finishTimestamp = networkMeter.stopPacketCapture()

            #
            # Fulfilling objects for data persistence
            #

            operation.meteringFinish = datetime.utcfromtimestamp(finishTimestamp).timestamp() # get utc format instead of time since epoch
            #getDatetimeFromTimestamp = datetime.fromtimestamp(operation.meteringFinish.timestamp()) # Use fromtimestamp instead of utcfromtimestamp
            actionReq = list(filter(lambda actionReq: actionReq.action.upper() == operationObject['operation'].upper(),
                self.openStackUtils.instanceAction.list(instanceServer)))[0]
            operation.openStackInfoStart = datetime.strptime(actionReq.start_time, START_TIME_FORMAT).timestamp()
            operation.openStackInfoFinish = datetime.strptime(instanceServer.updated,UTC_TIME_FORMAT).timestamp()
            operation.meteringDuration = operation.meteringFinish - operation.meteringStart
            operation.openStackInfoDuration = operation.openStackInfoFinish - operation.openStackInfoStart
            operationList.append(operation)
            if operation.meteringFinish < operation.openStackInfoFinish:
                print('ERROR: Network Meter stopped before the operation finished') #SHOULD LOG
                return
            if operation.meteringStart > operation.openStackInfoStart:
                print('ERROR: Network Meter started after the operation started') #SHOULD LOG
                return
        openSession.add_all(operationList)
        openSession.commit()
        openSession.close()
        instanceServer.force_delete()
        if not caching:
            self.openStackUtils.deleteImage(self.instanceImage)
            self.instanceImage = None
