from modules.loggers import *
import time
import itertools
import calendar
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from modules.openstack_utils import *
from modules.network_meter import *

#FIXME: Fix Object imports
#Objects must be imported somewhere else before induced life cycle starts
#Objects must be created at DB beforehand
from modules.objects import db_info
from modules.objects.execution import *
from modules.objects.operation import *
from modules.objects.metering import *
from modules.objects.service import *
from modules.objects.packet_info import *
from modules.objects.request_info import *
from modules.objects.os_image import *
from modules.objects import db_info as DB_INFO
#@TODO: proper indent too long lines

class InstanceLifeCycleMetering:
    autoId = itertools.count()
    def __init__(self, ifaceList=['lo'], imageInfo=None):
        if imageInfo is None:
            openSession = DB_INFO.getOpenSession()
            try:
                imageInfo = openSession.query(OsImage).first()
                openSession.close()
            except (NoResultFound, err):
                defaultLogger.error("Please, create at least one OsImage object")

        self.imageInfo = imageInfo
        self.ifaceList = ifaceList
        self.openStackUtils = OpenStackUtils() #use default authInfo
        self.instanceImage, self.networkId = self.prepareLifeCycleScenario(imageInfo)

    def prepareLifeCycleScenario(self, imageInfo):
        if not isinstance(imageInfo, OsImage):
            return (None,None)

        #create image and network
        cachedImage = self.openStackUtils.getImageByName(imageInfo.image_name)
        if cachedImage is None:
            defaultLogger.warning('Image cache is disabled!')
        self.instanceImage = cachedImage if cachedImage is not None else self.openStackUtils.createImage(imageInfo)
        self.networkId = self.openStackUtils.networkSetup()

        return (self.instanceImage, self.networkId)

    def startInducedLifeCycle(self, operationObjectList, caching=False):
        #
        # FIXME: Should delete all created instances before induced_life_cycle starts
        #
        if self.instanceImage is None or self.networkId is None:
            self.instanceImage, self.networkId = self.prepareLifeCycleScenario(self.imageInfo)
        if operationObjectList is None:
            defaultLogger.error("Please, provide operationObjectList")
            return None

        UTC_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
        START_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
        execution = Execution(imageId=self.imageInfo.image_id)

        openSession = DB_INFO.getOpenSession()

        openSession.add(execution)
        openSession.commit()#SQLAlchemy handles the ID auto increment

        fileList = [iface+'.pcap' for iface in self.ifaceList]
        instanceServer = None
        networkMeter = NetworkMeter(self.ifaceList,outputFileList=fileList)
        #Other infos about instanceServer -> instanceServer._info['OS-EXT-STS:vm_state']

        #
        # INDUCED LIFE CYCLE LOGIC
        #

        for operationObject in operationObjectList:
            defaultLogger.info('operation: %s started\n', operationObject['operation'])
            operation = Operation()
            operation.exec_id = execution.exec_id
            osImage = openSession.query(OsImage).get(execution.image_id)
            operation.type = operationObject['operation'].upper()
            startTimestamp = networkMeter.startPacketCapture(fileId=operationObject['operation'].upper() + '_' + osImage.image_name + '_' + str(execution.exec_id) + '_')
            operation.metering_start = datetime.utcfromtimestamp(startTimestamp).timestamp() # get utc format instead of time since epoch
            time.sleep(1) #tcpdump sync
            try:
                if operationObject['operation'].upper() == 'CREATE':
                    instanceServer = self.openStackUtils.createInstance('instanceServer',
                                    self.instanceImage, operationObject['params']['flavor'], self.networkId, computeType=True)
                else:
                    if instanceServer.status.upper() in operationObject['requiredStatus']:
                        defaultLogger.info('called anonymousFunction!\n')
                        operationObject['anonymousFunction'](self.openStackUtils.openstackConn.compute, instanceServer)
                    else:
                        defaultLogger.error('instanceServer\'s current status is not a required status for %s', operationObject['targetStatus'])
                        defaultLogger.error('You cannot make a server status move from %s to %s\n', instanceServer.status.upper(), operationObject['targetStatus'])
                        networkMeter.stopPacketCapture()
                        return None
                instanceServer = self.openStackUtils.openstackConn.compute.wait_for_server(instanceServer, status=operationObject['targetStatus'], interval=2, wait=240)
            except ValueError as error:
                defaultLogger.error(error)
                raise
            finishTimestamp = networkMeter.stopPacketCapture()
            defaultLogger.info('operation: %s finished\n', operationObject['operation'])
            defaultLogger.info('========================================================================\n\n')
            #
            # Fulfilling objects for data persistence
            #

            operation.metering_finish = datetime.utcfromtimestamp(finishTimestamp).timestamp() # get utc format instead of time since epoch
            #getDatetimeFromTimestamp = datetime.fromtimestamp(operation.metering_finish.timestamp()) # Use fromtimestamp instead of utcfromtimestamp
            actionReq = list(filter(lambda actionReq: actionReq.action.upper() == operationObject['operation'].upper(),
                self.openStackUtils.instanceAction.list(instanceServer)))[0]
            operation.openstack_info_start = datetime.strptime(actionReq.start_time, START_TIME_FORMAT).timestamp()
            operation.openstack_info_finish = datetime.strptime(instanceServer.updated,UTC_TIME_FORMAT).timestamp()
            operation.metering_duration = operation.metering_finish - operation.metering_start
            operation.openstack_info_duration = operation.openstack_info_finish - operation.openstack_info_start

            if operation.metering_finish < operation.openstack_info_finish:
                defaultLogger.error('ERROR: Network Meter stopped before the operation finished')
                return None
            if operation.metering_start > operation.openstack_info_start:
                defaultLogger.error('ERROR: Network Meter started after the operation started')
                return None


            openSession.add(operation)
            openSession.flush()
            [
                openSession.add(
                    Metering(parentId=operation.operation_id, iface=iface)
                )
                for iface in self.ifaceList
            ]

        openSession.commit()
        openSession.close()
        instanceServer.force_delete()
        if not caching:
            self.openStackUtils.deleteImage(self.instanceImage)
            self.instanceImage = None
