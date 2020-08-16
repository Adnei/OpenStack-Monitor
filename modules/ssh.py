from paramiko import SSHClient
import paramiko

class SSH:
    def __init__(self):
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname='myhostname', username='root', password='rootpassword')

    def exec_cmd(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        #0 will always be success. Other values mean different error codes
        if(stderr.channel.recv_exit_status() != 0 ):
            print(stderr.read())
        else:
            print(stdout.read()) 
