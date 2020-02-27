import time
import logging
from os import environ as env
from novaclient import client as novaClient
from keystoneauth1.identity import v3
from keystoneauth1 import session as keystoneSession
from glanceclient import Client as glanceClient
from neutronclient.v2_0 import client as neutronClient
from troveclient.v1 import client as troveClient

class OpenStackUtils:
    def __init__(self, authInfo=None, session=None):
            self.authInfo = authInfo
            self.session = session
            if self.session is None:
                self.session = authenticate(self.authInfo)
            self.glance = glanceClient('2',session=self.session)
            self.trove = troveClient(session=self.session)
            self.nova = novaClient.Client('2.1', session=self.session)
            self.neutron = neutronClient.Client(session=self.session)

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
        return keystoneSession.Session(auth=v3.Password(**authInfo))

    def createImage(self, data={'flavor':'m1.small', 'imagePath':'Fedora-Cloud-Base-31-1.9.x86_64.qcow2', 'imageName':'fedora31'}):
        image = self.glance.images.create(name=data['imageName'])
        self.glance.images.upload(image.id, open(data['imagePath'],'rb'))
        return image

    def deleteImage(self, imageRef):
        #not sure if it returns anything
        return self.glance.images.delete(imageRef.id)

    def createInstance(self, instanceName, glanceImage, flavorName='m1.small', nics=None):
        if nics is None:
            nics = 'none'
        novaFlavor = self.nova.flavors.find(name=flavorName)

        return self.nova.servers.create(instanceName, glanceImage, novaFlavor, nics=nics)

    def networkSetup(self):
        # https://developer.openstack.org/api-ref/network/v2/#create-network
        network_request = {
            'network': {
                'name': 'local',
                'admin_state_up': True
            }
        }

        response = self.neutron.create_network(network_request)
        network_id = response['network']['id']
        nics = [{'net-id': network_id}]

        # https://developer.openstack.org/api-ref/network/v2/#create-subnet
        subnet_request = {
            "subnet": {
                "name": "Subnet1",
                "network_id": network_id,
                "ip_version": 4,
                "cidr": "192.168.0.0/24"
            }
        }
        self.neutron.create_subnet(subnet_request)
        return nics

    # def troveGetInstance(self, instanceId):
    #     return self.trove.instances.get(instanceId)
