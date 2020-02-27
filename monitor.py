from modules.network_meter import *
from modules.induced_life_cycle import *
import time
import sys, getopt


#@TODO: proper indent too long lines

def main(argv):

    # @TODO
    #   FIX argv PARAMETERS

    instanceLifeCycleMetering = InstanceLifeCycleMetering(ifaceList=argv)
    instanceLifeCycleMetering.prepareLifeCycleScenario()
    instanceLifeCycleMetering.startInducedLifeCycle()

if __name__ == "__main__":
   main(sys.argv[1:])
