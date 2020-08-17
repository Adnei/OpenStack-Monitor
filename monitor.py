import vm_operation as VM_OPERATION
from modules.schema_loader import *
import modules.utils as UTILS

# FIXME: These imports are really bad (all the way through the project).
#    Avoid importing all ( * ) from a module. It makes the code confuse to read:
#           *  "Where did this method came from ?"
#           *  "I can't see where this variable is created"
#    To avoid this kinda confusion you should specify the module you're importing shit from :)
#    EX: import modules.utils as UTILS
#    Then call a method from utils like this: UTILS.getServices() --> See? We know getServices came from UTILS :) (rpple)
from modules.loggers import *
from modules.network_meter import *
from modules.induced_life_cycle import *
from modules.packet_analysis import *

import time
import sys, getopt

def main(argv):

    # @TODO
    #   FIX argv PARAMETERS
    #   Parameterize NICs, file names, number of execution and image infos

    osList = UTILS.createOsImage([
        # {
        #     'imagePath':'Fedora-Cloud-Base-31-1.9.x86_64.qcow2',
        #     'imageName':'fedora31',
        #     'username' :'fedora'
        # },
        {
            'imagePath':'Fedora-Cloud-Base-32-1.6.x86_64.qcow2',
            'imageName':'fedora32',
            'username' :'fedora'
        },
        # {
        #     'imagePath':'FreeBSD-12.0-RELEASE-amd64.qcow2.xz',
        #     'imageName':'freebsd12'
        # }
        # {
        #     'imagePath':'focal-server-cloudimg-amd64.img',
        #     'imageName':'focal_ubuntu',
        #     'username' :'ubuntu'
        # },
        # {
        #     'imagePath':'bionic-server-cloudimg-amd64.img',
        #     'imageName':'bionic_ubuntu',
        #     'username' :'ubuntu'
        # },
        # {
        #     'imagePath':'CentOS-7-x86_64-GenericCloud.qcow2',
        #     'imageName':'centos7_light',
        #     'username' :'centos'
        # },
        # {
        #     'imagePath':'CentOS-7-x86_64-GenericCloud-1707.qcow2',
        #     'imageName':'centos7',
        #     'username' :'centos'
        # },
        # {
        #     'imagePath':'debian-10-openstack-amd64.qcow2',
        #     'imageName':'debian10qcow2',
        #     'username' :'debian'
        # },
        # {
        #     'imagePath':'cirros-0.4.0-aarch64-disk.img',
        #     'imageName':'cirros',
        #     'username' :'cirros'
        # },
        # {
        #     'imagePath':'debian-10-openstack-amd64.raw',
        #     'imageName':'debian10raw',
        #     'imageFormat': 'raw'
        # },
        # {
        #     'imagePath':'windows_server.qcow2.gz',
        #     'imageName':'windows_server',
        #     'imageFormat': 'qcow2'
        # }
    ])

    if osList is None:
        defaultLogger.critical('Aborting! Impossible to create VMs. No images')
        return None

    defaultServices = [ Service(serviceName=service) for service in list(UTILS.SERVICES_MAP.keys())]
    openSession = DB_INFO.getOpenSession()
    openSession.add_all(defaultServices)
    openSession.commit()
    openSession.close()

    for osImage in osList:
        instanceLifeCycleMetering = InstanceLifeCycleMetering(ifaceList=argv, imageInfo=osImage)
        for idx in range(1,31): #Do N executions
            execution = instanceLifeCycleMetering.startInducedLifeCycle(VM_OPERATION.operationObjectList)
            openSession = DB_INFO.getOpenSession()
            try:
                meteringList = openSession.query(
                    Metering
                ).join(
                    Operation
                ).join(
                    Execution
                ).filter(
                    Execution.exec_id == execution.exec_id
                ).all()
                if meteringList is None or len(meteringList) == 0:
                    raise ValueError('No Metering found for execution id %s ', execution.exec_id)
                analysisList = [TrafficAnalysis(metering) for metering in meteringList]
                count=0
                for trafficAnalysis in analysisList:
                    defaultLogger.info("Traffic analysis started\nAnalysing metering id: %s", str(trafficAnalysis.meteringObj.metering_id))
                    defaultLogger.info("Working on %s file", trafficAnalysis.pcapFile)
                    count+=1
                    ignoredPacketsCounter = trafficAnalysis.runAnalysis()
                    if ignoredPacketsCounter > 0:
                        defaultLogger.critical('Ignored packtes %s', str(ignoredPacketsCounter))
                    else:
                        defaultLogger.info('Ignored packtes %s', str(ignoredPacketsCounter))
                    #TODO Parameterize - Debugging mode should not delete PCAP files
                    UTILS.deleteFile(trafficAnalysis.pcapFile)
                    # UTILS.deleteFile(trafficAnalysis.lsofFile)
            except ValueError as error:
                defaultLogger.error(error)
                raise

if __name__ == "__main__":
    #NICS
    main(sys.argv[1:])
