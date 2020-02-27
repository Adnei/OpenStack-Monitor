from modules.network_meter import *
from modules.induced_life_cycle import *
import time
import sys, getopt


def main(argv):

    # @TODO
    #   FIX argv PARAMETERS

    instanceLifeCycleMetering = InstanceLifeCycleMetering(ifaceList=argv)


if __name__ == "__main__":
   main(sys.argv[1:])
