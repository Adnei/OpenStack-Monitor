from modules.loggers import *
from paramiko import SSHClient
import paramiko
import os

class SSH:
    def __init__(self):
        self.sshClient = SSHClient()
        # self.sshClient.load_system_host_keys()

    def ssh_connect(self, hostname, username, privateKeyPath, publicKeyPath):
        self.privateKeyPath = privateKeyPath
        self.publicKeyPath = publicKeyPath
        self.hostname = hostname
        self.username = username
        if not os.path.isfile(os.path.expanduser(privateKeyPath)) or os.path.isfile(os.path.expanduser(publicKeyPath)):
            self._generateKeyPair(privateKeyPath, publicKeyPath)
        self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshClient.connect(hostname=self.hostname, username=self.username, key_filename=self.privateKeyPath)

    def exec_cmd(self, cmd):
        stdin, stdout, stderr = self.sshClient.exec_command(cmd)
        try:
            #0 will always be success. Other values mean different error codes
            if(stderr.channel.recv_exit_status() != 0 ):
                raise ValueError('Command on remote host returned error: ', stderr.read())
            return stdout
        except ValueError as error:
            defaultLogger.error(error)

    def generateKeyPair(self, privateFilePath, publicFilePath):
        """
            Generate key pair for ssh. Based on https://programtalk.com/vs2/python/11028/acs-cli/acs/acs.py/
        """
        (sshDir, privateFileName) = os.path.split(os.path.expanduser(privateFilePath))
        if not os.path.exists(sshDir):
            os.makedirs(sshDir)
        key = paramiko.RSAKey.generate(1024)
        key.write_private_key_file(os.path.expanduser(privateFilePath))
        with open(os.path.expanduser(publicFilePath),'w') as public:
            public.write('%s %s' % (key.get_name(), key.get_base64()))
