from modules.loggers import *
from paramiko import SSHClient
import paramiko
import os

class SSH:
    def __init__(self, hostname, username, privateKeyPath):
        self.privateKeyPath = os.path.expanduser(privateKeyPath)
        self.hostname = hostname
        self.username = username
        self.sshClient = SSHClient()
        # self.sshClient.load_system_host_keys()

    def ssh_connect(self):

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
