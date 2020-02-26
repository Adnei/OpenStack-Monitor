from modules.network_meter import *
from modules.induced_life_cycle import *
import time
import sys, getopt


def main(argv):

    # @TODO
    #   FIX PARAMETERS
    fileList = [iface+'.pcap' for iface in argv] #['enp3s0.pcap','lo.pcap']
    networkMeter = NetworkMeter(ifaceList=argv,outputFileList=fileList)
    networkMeter.startPacketCapture()
    print(argv)
    print(fileList)
    #do scenario
    #default state list ['create','suspend','resume','stop','shelve']
    instanceLifeCycle = InstanceLifeCycle()
    instanceLifeCycle.startInducedLifeCycle()
    time.sleep(10) #for the sake of testing :)
    networkMeter.stopPacketCapture()

if __name__ == "__main__":
   main(sys.argv[1:])
