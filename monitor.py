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
            'requiredStatus':['BUILD'], #Note: OpenStack should refactor this state to INITIALIZE
            'params':{'flavor':'m1.small'},
            'startedAt': None, # Will be removed
            'finishedAt': None, # Will be removed
            'elapsedSecs': None # Will be removed
        },
        {
            'operation':'SUSPEND',
            'targetStatus':'SUSPENDED',
            'requiredStatus':['ACTIVE','SHUTOFF'],
            'anonymousFunction':lambda instance: instance.suspend(),
            'startedAt': None,
            'finishedAt': None,
            'elapsedSecs': None
        },
        {
            'operation':'RESUME',
            'targetStatus':'ACTIVE',
            'requiredStatus':['SUSPENDED'],
            'anonymousFunction':lambda instance: instance.resume(),
            'startedAt': None,
            'finishedAt': None,
            'elapsedSecs': None
        },
        {
            'operation':'STOP',
            'targetStatus':'SHUTOFF', #STOPPED
            'requiredStatus':['ACTIVE','SHUTOFF', 'RESCUED'],
            'anonymousFunction':lambda instance: instance.stop(),
            'startedAt': None,
            'finishedAt': None,
            'elapsedSecs': None
        },
        {
            'operation':'SHELVE',
            'targetStatus':'SHELVED_OFFLOADED',
            'requiredStatus':['ACTIVE', 'SHUTOFF', 'SUSPENDED'],
            'anonymousFunction':lambda instance: instance.shelve(),
            'startedAt': None,
            'finishedAt': None,
            'elapsedSecs': None
        }
    ]

    instanceLifeCycleMetering = InstanceLifeCycleMetering(ifaceList=argv)
    instanceLifeCycleMetering.startInducedLifeCycle(operationObjectList)

if __name__ == "__main__":
   main(sys.argv[1:])
