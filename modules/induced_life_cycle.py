import time
import logging
from os import environ as env
from novaclient import client as novaclient

from keystoneauth1.identity import v3
from keystoneauth1 import session
from glanceclient import Client as glanceclient
from neutronclient.v2_0 import client as neutronclient


class InstanceLifeCycle:
    def __init__(self, authInfo=None, instanceInfo=None, stateList=['create', 'suspend','resume','stop','shelve']):
        def authenticate(authInfo):
            if authInfo is None:
                #this requires the [machine] user to be stated as an OpenStack admin (admin-openrc.sh file)
                #see docs.openstack.org/liberty/install-guide-ubuntu/keystone-openrc.html
                authInfo = {
                    'auth_url': env['OS_AUTH_URL'],
                    'username': env['OS_USERNAME'],
                    'password': env['OS_PASSWORD'],
                    'project_name': env['OS_PROJECT_NAME'],
                    'user_domain_name': env['OS_USER_DOMAIN_NAME'],
                    'project_domain_name': env['OS_PROJECT_DOMAIN_NAME']
                }
            return session.Session(auth=v3.Password(**authInfo))

        self.stateList = stateList
        self.authInfo = authInfo
        self.instanceInfo = instanceInfo
        self.authSession = authenticate(self.authInfo)


    def startInducedLifeCycle(self):
        if self.authSession is None:
            print("authSession == None")
        print(self.authSession)
