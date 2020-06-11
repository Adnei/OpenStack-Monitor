import subprocess as sub
import os
import time
from modules.loggers import *

#@TODO: proper indent too long lines
#@TODO: Use pyshark instead of tcpdump
#       It will do the same thing, but with a python wrapper
#@TODO --> Document me :)
class NetworkMeter:
    def __init__(self, ifaceList=['lo'], outputFileList=['lo.pcap'], lsofTemp='/proj/labp2d-PG0/lsof_temp'):
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
            command = 'exec tcpdump -i '+capture['iface']+' -nn -s 0 -w ' + fileId + capture['file']
            capture['process'], ts = self.__startProcess(command)
        return ts

    def stopPacketCapture(self):
        for capture in self.captureList:
            capture['process'] = self.__stopProcess(capture['process'])
        return time.time()

    def startListFiles(self, tempFilePath='lsof_temp'):
        lsofProc = 'lsof -r 1 -i :5672 >>' + tempFilePath
        return self.__startProcess(lsofProc)

    def stopListFiles(self, process, resultFile, tempFilePath='lsof_temp'):
        #Sometimes the operation is too fast and lsof is still in its first iteration.
        #Thus we wait until it finishes at least the first iteration
        if(os.stat(lsofTempFile).st_size == 0):
            defaultLogger.critical('%s could not be created!! Temp file was still empty. Waiting for LSOF.')
            time.sleep(1)
            return stopListFiles(process, resultFile, tempFilePath=tempFilePath)

        self.__stopProcess(process)
        removeDuplicated = "awk '!/./ || !seen[$0]++' "+tempFilePath+" > " + resultFile
        removeProc, ts = self.__startProcess(removeDuplicated)
        removeProc.wait()
        try:
            os.remove(tempFilePath)
        except OSError as error:
            defaultLogger.error(error)
            raise
        return True

    def __startProcess(self, command, shell=True, stdout=sub.DEVNULL):
        process = sub.Popen(command, shell=shell, stdout=stdout)
        ts = time.time()
        return (process, ts)

    def __stopProcess(self, proc):
        if proc is not None:
            proc.terminate()
            proc.wait()
        return None
