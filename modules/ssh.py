from modules.loggers import *
from paramiko import SSHClient
import paramiko
from os import environ as env

class SSH:
    def __init__(self, hostname):
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname='', username='ubuntu', password=env['VMPSSWD'])

    def exec_cmd(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        try:
            #0 will always be success. Other values mean different error codes
            if(stderr.channel.recv_exit_status() != 0 ):
                raise ValueError('Command on remote host returned error: ', stderr.read())
            return stdout
        except ValueError as error:
            defaultLogger.error(error)
