from modules.network_meter import *
from modules.induced_life_cycle import *
import time
import sys, getopt


#@TODO: proper indent too long lines

def main(argv):

    # @TODO
    #   FIX argv PARAMETERS
    #   Parameterize NICs, file names and number of execution

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
    # @FIXME: Should be able to start N induced life cycles without having to instantiate a new InstanceLifeCycleMetering everytime.
    # Look at prepareLifeCycleScenario and image caching.
    for idx in range(1,5): #Do N times
        instanceLifeCycleMetering = InstanceLifeCycleMetering(ifaceList=argv)
        instanceLifeCycleMetering.startInducedLifeCycle(operationObjectList)

if __name__ == "__main__":
   main(sys.argv[1:])
