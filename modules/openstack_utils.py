import time
# import logging
from os import environ as env
from novaclient import client as novaClient
from keystoneauth1.identity import v3
from keystoneauth1 import session as keystoneSession
from glanceclient import Client as glanceClient
from neutronclient.v2_0 import client as neutronClient
from troveclient.v1 import client as troveClient

#@TODO: proper indent too long lines

class OpenStackUtils:
    def __init__(self, authInfo=None, session=None):
            self.authInfo = authInfo
            self.session = session
            if self.session is None:
                self.session = self.authenticate(self.authInfo)
            self.glance = glanceClient('2',session=self.session)
            self.trove = troveClient.Client(session=self.session)
            self.nova = novaClient.Client('2.1', session=self.session)
            self.instanceAction = self.nova.instance_action
            self.neutron = neutronClient.Client(session=self.session)

    def authenticate(self, authInfo=None):
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

    def createImage(self, data={'imagePath':'Fedora-Cloud-Base-31-1.9.x86_64.qcow2',
        'imageName':'fedora31', 'imageFormat':'qcow2',
        'imageContainer':'bare'}):
        image = self.glance.images.create(name=data['imageName'],
            container_format=data['imageContainer'],
            disk_format=data['imageFormat'])
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

    # Workaround, since documentation doesn't provide enough information about a get operation by image name
    # @TODO: Refactor ASAP
    # Serious performance issue
    def getImageByName(self, name):
        imageList = self.glance.images.list()
        filteredImageList = list(filter(lambda image: image.name == name, imageList))
        if len(filteredImageList) == 0 :
            return None
        return filteredImageList[0]

    def networkSetup(self):
        localNetworks = self.neutron.list_networks(name='local')

        if len(localNetworks['networks']) > 0:
            networkId = localNetworks['networks'][0]['id']
            nics = [{'net-id' : networkId}]
        else:
            # https://developer.openstack.org/api-ref/network/v2/#create-network
            networkRequest = {
                'network': {
                    'name': 'local',
                    'admin_state_up': True
                }
            }

            response = self.neutron.create_network(networkRequest)
            networkId = response['network']['id']
            nics = [{'net-id': networkId}]

            # https://developer.openstack.org/api-ref/network/v2/#create-subnet
            subnetRequest = {
                "subnet": {
                    "name": "Subnet1",
                    "network_id": networkId,
                    "ip_version": 4,
                    "cidr": "192.168.0.0/24"
                }
            }
            self.neutron.create_subnet(subnetRequest)
        return nics
