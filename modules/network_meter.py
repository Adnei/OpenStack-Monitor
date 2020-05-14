import subprocess as sub
import time

#@TODO: proper indent too long lines
#@TODO: Use pyshark instead of tcpdump
#       It will do the same thing, but with a python wrapper
class NetworkMeter:
    def __init__(self, ifaceList=['lo'], outputFileList=['lo.pcap']):
        if len(ifaceList) != len(outputFileList):
            ifaceList = ['lo']
            outputFileList = ['lo.pcap']

        self.captureList = [
            {
                'iface':iface,
                'file':outputFileList[idx], 'process':None
            }
            for idx, iface in enumerate(ifaceList)
        ]

    def startPacketCapture(self, fileId=''):
        #https://serverfault.com/questions/805006/tcpdump-on-multiple-interfaces
        #The flags -nn turns off dns resolution for speed, -s 0 saves the full packet and -w writes to a file.
        for capture in self.captureList:
            capture['process'] = sub.Popen('exec tcpdump -i '+capture['iface']+' -nn -s 0 -w ' + fileId + capture['file'],
                shell=True,
                stdout=sub.DEVNULL)
        return time.time()

    def stopPacketCapture(self):
        for capture in self.captureList:
            if capture['process'] is not None:
                capture['process'].terminate()
                capture['process'].wait()
                capture['process'] = None
        return time.time()