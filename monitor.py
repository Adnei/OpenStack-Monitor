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
            'targetState':'ACTIVE',
            'requiredState':['BUILD'], #Note: OpenStack should refactor this state to INITIALIZE
            'params':{'flavor':'m1.small'},
            'startedAt': None,
            'finishedAt': None,
            'elapsedSecs': None
        },
        {
            'operation':'SUSPEND',
            'targetState':'SUSPENDED',
            'requiredState':['ACTIVE','SHUTOFF'],
            'anonymousFunction':lambda instance: instance.suspend(),
            'startedAt': None,
            'finishedAt': None,
            'elapsedSecs': None
        },
        {
            'operation':'RESUME',
            'targetState':'ACTIVE',
            'requiredState':['SUSPENDED'],
            'anonymousFunction':lambda instance: instance.resume(),
            'startedAt': None,
            'finishedAt': None,
            'elapsedSecs': None
        },
        {
            'operation':'STOP',
            'targetState':'STOPPED',
            'requiredState':['ACTIVE','SHUTOFF', 'RESCUED'],
            'anonymousFunction':lambda instance: instance.stop(),
            'startedAt': None,
            'finishedAt': None,
            'elapsedSecs': None
        },
        {
            'operation':'SHELVE',
            'targetState':'SHELVED_OFFLOADED',
            'requiredState':['ACTIVE', 'SHUTOFF', 'SUSPENDED'],
            'anonymousFunction':lambda instance: instance.shelve(),
            'startedAt': None,
            'finishedAt': None,
            'elapsedSecs': None
        }
    ]

    instanceLifeCycleMetering = InstanceLifeCycleMetering(ifaceList=argv)
    instanceLifeCycleMetering.startInducedLifeCycle()

if __name__ == "__main__":
   main(sys.argv[1:])
