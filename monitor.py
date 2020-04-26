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
# from modules.objects.os_image import *
from modules.network_meter import *
from modules.induced_life_cycle import *
# from modules.objects import db_info as DB_INFO
from modules.packet_analysis import *
# from modules.objects.service import *

import time
import sys, getopt

def main(argv):

    # @TODO
    #   FIX argv PARAMETERS
    #   Parameterize NICs, file names, number of execution and image infos

    osList = UTILS.createOsImage([
        {
            'imagePath':'Fedora-Cloud-Base-31-1.9.x86_64.qcow2',
            'imageName':'fedora31'
        },
        {
            'imagePath':'focal-server-cloudimg-amd64.img',
            'imageName':'focal_ubuntu'
        },
        {
            'imagePath':'bionic-server-cloudimg-amd64.img',
            'imageName':'bionic_ubuntu'
        },
        {
            'imagePath':'CentOS-7-x86_64-GenericCloud.qcow2',
            'imageName':'centos7_light'
        },
        # {
        #     'imagePath':'CentOS-7-x86_64-GenericCloud-1707.qcow2',
        #     'imageName':'centos7'
        # },
        # {
        #     'imagePath':'debian-10-openstack-amd64.qcow2',
        #     'imageName':'debian10_qcow2'
        # },
        {
            'imagePath':'cirros-0.4.0-aarch64-disk.img',
            'imageName':'cirros'
        }#,
        # {
        #     'imagePath':'debian-10-openstack-amd64.raw',
        #     'imageName':'debian10_raw',
        #     'imageFormat': 'raw'
        # }
    ])

    if osList is None:
        defaultLogger.critical('Aborting! Impossible to create VMs. No images')
        return None

    for osImage in osList:
        instanceLifeCycleMetering = InstanceLifeCycleMetering(ifaceList=argv, imageInfo=osImage)
        for idx in range(1,6): #Do N times
            instanceLifeCycleMetering.startInducedLifeCycle(VM_OPERATION.operationObjectList)

    openSession = DB_INFO.getOpenSession()
    meteringList = openSession.query(Metering).all()
    openSession.close()

    defaultServices = [ Service(serviceName=service) for service in list(UTILS.SERVICES_MAP.keys())]
    openSession = DB_INFO.getOpenSession()
    openSession.add_all(defaultServices)
    openSession.commit()
    openSession.close()

    analysisList = [TrafficAnalysis(metering) for metering in meteringList]
    count=0
    for trafficAnalysis in analysisList:
        defaultLogger.info("Traffic analysis started\nAnalysing metering id: %s", str(trafficAnalysis.meteringObj.metering_id))
        count+=1
        ignoredPacketsCounter = trafficAnalysis.runAnalysis()
        #
        # FIXME: Log ignored packets from which analysis --> report which execution, operation, etc...
        #       Need detailed info
        if ignoredPackets > 0:
            defaultLogger.critical('Ignored packtes %s', str(ignoredPacketsCounter))
        else:
            defaultLogger.info('Ignored packtes %s', str(ignoredPacketsCounter))

if __name__ == "__main__":
    #NICS
    main(sys.argv[1:])
