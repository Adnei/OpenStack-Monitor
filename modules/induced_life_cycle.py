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
    """
        This class represents a 'monitored instance life cycle'

        The specified life cycle (vm_operation.py) will be executed and the traffic will be captured

        Attributes:
                    ifaceList (array of string)
                    imageInfo (<OsImage> --> see objects/os_image.py )
                    openStackUtils (<OpenStackUtils> --> see openstack_utils.py)
                    instanceImage (OpenStack Glance Image object)
                    networkId (OpenStack uuid for network)
    """
    autoId = itertools.count()
    def __init__(self, ifaceList=['lo'], imageInfo=None):
        """
            Instantiating a 'monitored instance life cycle' takes a list of interfaces to be monitored and information about the image used for the instance server

            Parameters: ifaceList (array of string): list of interfaces to be monitored. Defaults to loopback interface
                        imageInfo (<OsImage> --> see objects/os_image.py): Object that represents an image to be used for the instance server.
                            If none is provided, it will use the first persisted OsImage in the database.
                            If none persisted OsImages, returns error 'Please, create at least one OsImage object'
        """
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
        """
            Checks for cached images and network setups. Creates them if none cached were found.
            Most times its called only when instantiating a InstanceLifeCycleMetering class

            Parameters:
                        imageInfo (<OsImage> --> see objects/os_image.py): Object that represents an image to be used for the instance server.

            Returns:
                        tuple -> (instanceImage, networkId): OpenStack Glance image and network uuid respectively
        """
        if not isinstance(imageInfo, OsImage):
            return (None,None)
        cachedImage = self.openStackUtils.getImageByName(imageInfo.image_name)
        if cachedImage is None:
            defaultLogger.warning('Image cache is disabled!')
        self.instanceImage = cachedImage if cachedImage is not None else self.openStackUtils.createImage(imageInfo)
        self.networkId = self.openStackUtils.networkSetup()

        return (self.instanceImage, self.networkId)

    def startInducedLifeCycle(self, operationObjectList, imageCaching=False):
        """
            Executes the specified life cycle ( in vm_operation.py).
            It takes the servers through all specified states. It only does allowed state transitions. Please, refer to https://docs.openstack.org/nova/latest/reference/vm-states.html

            Parameters:
                        operationObjectList (see vm_operation.py): list of operations to be executed against the server
                        imageCaching (Boolean): Flag that sets ON or OFF the image caching
        """


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
        computeInstanceServer = None
        networkMeter = NetworkMeter(self.ifaceList,outputFileList=fileList)

        #
        # INDUCED LIFE CYCLE LOGIC
        #

        for operationObject in operationObjectList:
            defaultLogger.info('operation: %s started\n', operationObject['operation'])
            operation = Operation()
            operation.exec_id = execution.exec_id
            osImage = openSession.query(OsImage).get(execution.image_id)
            operation.type = operationObject['operation'].upper()
            lsofTempFile = '/proj/labp2d-PG0/temp_lsof'
            lsofProc, lsofTs = networkMeter.startListFiles(tempFilePath=lsofTempFile)
            startTimestamp = networkMeter.startPacketCapture(fileId=operationObject['operation'].upper() + '_' + osImage.image_name + '_' + str(execution.exec_id) + '_')
            operation.metering_start = datetime.utcfromtimestamp(startTimestamp).timestamp() # get utc format instead of time since epoch
            time.sleep(1) #tcpdump sync

            try:
                if operationObject['operation'].upper() == 'CREATE':
                    computeInstanceServer = self.openStackUtils.createInstance('computeInstanceServer',
                                    self.instanceImage, operationObject['params']['flavor'], self.networkId, computeType=True)
                else:
                    if computeInstanceServer.status.upper() in operationObject['requiredStatus']:
                        defaultLogger.info('called anonymousFunction!\n')
                        operationObject['anonymousFunction'](self.openStackUtils.openstackConn.compute, computeInstanceServer)
                    else:
                        defaultLogger.error('computeInstanceServer\'s current status is not a required status for %s', operationObject['targetStatus'])
                        defaultLogger.error('You cannot make a server status move from %s to %s\n', computeInstanceServer.status.upper(), operationObject['targetStatus'])
                        networkMeter.stopPacketCapture()
                        return None
                computeInstanceServer = self.openStackUtils.openstackConn.compute.wait_for_server(computeInstanceServer, status=operationObject['targetStatus'], interval=2, wait=240)
            except ValueError as error:
                defaultLogger.error(error)
                raise

            finishTimestamp = networkMeter.stopPacketCapture()
            resultLsofFile = 'lsof_'+operationObject['operation'].upper() + '_' + osImage.image_name + '_' + str(execution.exec_id)
            stoppedLsof = networkMeter.stopListFiles(lsofProc, resultLsofFile, tempFilePath=lsofTempFile)
            operation.metering_finish = datetime.utcfromtimestamp(finishTimestamp).timestamp() # get utc format instead of time since epoch
            defaultLogger.info('operation: %s finished\n', operationObject['operation'])
            defaultLogger.info('========================================================================\n\n')
            self.__persistOperationMetering(operation, computeInstanceServer, operationObject, START_TIME_FORMAT, UTC_TIME_FORMAT)

        novaServer.force_delete()
        if not imageCaching:
            self.openStackUtils.deleteImage(self.instanceImage)
            self.instanceImage = None
        openSession.close()

        return execution


    def __persistOperationMetering(self, operation, computeInstanceServer, operationObject, START_TIME_FORMAT, UTC_TIME_FORMAT):
        openSession = DB_INFO.getOpenSession()
        """
            Persists Operation and its Meterings.
            Used as auxiliar function. Should not be called from outside
        """

        #####################################################################################################################
        # OpenStack list instance actions.                                                                                  #
        # Due to a FIXME inside the get instance action, this workaround was implemented                                    #
        # It lists all the actions executed to the instance and filters searching by the current operation being persisted  #
        #####################################################################################################################
        actionReq = list(filter(lambda actionReq: actionReq.action.upper() == operationObject['operation'].upper(),
            self.openStackUtils.instanceAction.list(computeInstanceServer)))[0]
        #####################################################################################################################
        operation.openstack_info_start = datetime.strptime(actionReq.start_time, START_TIME_FORMAT).timestamp()
        operation.openstack_info_finish = datetime.strptime(computeInstanceServer.updated_at, UTC_TIME_FORMAT).timestamp()
        operation.metering_duration = operation.metering_finish - operation.metering_start
        operation.openstack_info_duration = operation.openstack_info_finish - operation.openstack_info_start
        if operation.metering_finish < operation.openstack_info_finish:
            defaultLogger.error('ERROR: Network Meter stopped before the operation finished')
            #FIXME Should throw error
            return None
        if operation.metering_start > operation.openstack_info_start:
            defaultLogger.error('ERROR: Network Meter started after the operation started')
            #FIXME Should throw error
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
