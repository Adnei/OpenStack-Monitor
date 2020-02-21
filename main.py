from modules.network_meter import *
import time

#@TODO:
#      parameterize ifaces and files
networkMeter = NetworkMeter(['enp3s0','lo'],['enp3s0.pcap','lo.pcap'])
networkMeter.startPacketCapture()
#do scenario
#inducedLifeCycle = InducedLifeCycle(['create','suspend','resume','stop','shelve'])
networkMeter.stopPacketCapture()
