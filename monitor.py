from modules.loggers import *
from modules.network_meter import *
from modules.induced_life_cycle import *
from modules.objects import db_info as DB_INFO
from modules.packet_analysis import *
from modules.objects.service import *
import time
import sys, getopt


#@TODO: proper indent too long lines

def main(argv):

    # @TODO
    #   FIX argv PARAMETERS
    #   Parameterize NICs, file names, number of execution and image infos

    operationObjectList = [
        {
            'operation':'CREATE',
            'targetStatus':'ACTIVE',
            'requiredStatus':['BUILD'], #Note: OpenStack should refactor this status to INITIALIZE
            'params':{'flavor':'m1.small'}
        },
        {
            'operation':'SUSPEND',
            'targetStatus':'SUSPENDED',
            'requiredStatus':['ACTIVE','SHUTOFF'],
            'anonymousFunction':lambda instance: instance.suspend()
        },
        {
            'operation':'RESUME',
            'targetStatus':'ACTIVE',
            'requiredStatus':['SUSPENDED'],
            'anonymousFunction':lambda instance: instance.resume()
        },
        {
            'operation':'STOP',
            'targetStatus':'SHUTOFF', #STOPPED
            'requiredStatus':['ACTIVE','SHUTOFF', 'RESCUED'],
            'anonymousFunction':lambda instance: instance.stop()
        },
        {
            'operation':'SHELVE',
            'targetStatus':'SHELVED_OFFLOADED',
            'requiredStatus':['ACTIVE', 'SHUTOFF', 'SUSPENDED'],
            'anonymousFunction':lambda instance: instance.shelve()
        }
    ]
    instanceLifeCycleMetering = InstanceLifeCycleMetering(ifaceList=argv)
    for idx in range(1,2): #Do N times
        instanceLifeCycleMetering.startInducedLifeCycle(operationObjectList)

    initSession = DB_INFO.SESSIONMAKER(bind=DB_INFO.ENGINE)
    openSession = initSession()
    meteringList = openSession.query(Metering).all()
    openSession.close()

    defaultServices = [ Service(serviceName=service) for service in [  'nova',
                                                                'keystone',
                                                                'swift',
                                                                'glance',
                                                                'cinder',
                                                                'neutron' ]]
    openSession = initSession()
    openSession.add_all(defaultServices)
    openSession.commit()
    openSession.close()

    analysisList = [TrafficAnalysis(metering) for metering in meteringList]
    count=0
    for trafficAnalysis in analysisList:
        print("executing analysis -> ", count)
        count+=1
        ignoredPacketsCounter = trafficAnalysis.runAnalysis()
        defaultLogger.critical('Ignored packtes %s', str(ignoredPacketsCounter))

if __name__ == "__main__":
   main(sys.argv[1:])
