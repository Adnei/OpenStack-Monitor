import subprocess as sub
import os
import time
import signal
from modules.loggers import *
import modules.utils as UTILS

#@TODO: proper indent too long lines
#@TODO: Use pyshark instead of tcpdump
#       It will do the same thing, but with a python wrapper
#@TODO --> Document me :)
#@FIXME avoid the use of shell=True when working with subprocess
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
        fileObject = open(tempFilePath, 'w')
        lsofProc = 'lsof -r 1 -i :5672'
        # proc, ts = self.__startProcess(lsofProc, preexec_fn=os.setsid, stdout=fileObject)
        # proc, ts = self.__startProcess(lsofProc, stdout=fileObject, start_new_session=True)
        proc, ts = self.__startProcess(lsofProc, stdout=fileObject)
        defaultLogger.info('lsof started. Storing at %s. PID = %s, timestamp = %s',tempFilePath, proc.pid, ts)
        return (proc, ts, fileObject)

    def stopListFiles(self, process, resultFile, fileObject):
        tempFilePath = fileObject.name
        #Sometimes the operation is too fast and lsof is still in its first iteration.
        #Thus we wait until it finishes at least the first iteration
        if(os.path.isfile(tempFilePath) == False or os.stat(tempFilePath).st_size == 0):
            defaultLogger.critical('%s (temp file) is empty!! ',tempFilePath)
            defaultLogger.critical('%s could not be created!! Temp file was still empty. Waiting for LSOF.',resultFile)
            time.sleep(1)
            return self.stopListFiles(process, resultFile, fileObject)

        # self.__stopProcess(process)
        #This is a workaround to stop all the background processes
        #FIXME should do it inside a try catch and log errors nicely
        # os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        os.kill(process.pid, signal.SIGINT) # like pressing CTRL + C
        fileObject.close()
        removeDuplicated = "awk '!/./ || !seen[$0]++' "+tempFilePath+" > " + resultFile
        removeProc, ts = self.__startProcess(removeDuplicated)
        removeProc.wait()

        return UTILS.deleteFile(tempFilePath)


    def __startProcess(self, command, shell=True, stdout=sub.DEVNULL, start_new_session=False):
        process = sub.Popen(command, shell=shell, stdout=stdout, start_new_session=start_new_session)
        ts = time.time()
        return (process, ts)

    def __stopProcess(self, proc):
        if proc is not None:
            proc.terminate()
            proc.wait()
        return None
