import time
# import logging
from os import environ as env
from novaclient import client as novaClient
from keystoneauth1.identity import v3
from keystoneauth1 import session as keystoneSession
from glanceclient import Client as glanceClient
from neutronclient.v2_0 import client as neutronClient
from troveclient.v1 import client as troveClient
from openstack import connection
from modules.objects.os_image import *

#@TODO: proper indent too long lines

class OpenStackUtils:
    """
        Utils class for OpenStack interaction

        Attributes: authInfo (authentication object. See authenticate method)
                    session (authenticated session)
                    glance (glance object)
                    trove (trove object)
                    nova (nova object)
                    instanceAction (shortcut for nova.instance_action object)
                    neutron (neutron object)
                    openstackConn (compute api connection object)
    """

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
            self.openstackConn = connection.Connection(session=self.session, compute_api_version='2')

    def authenticate(self, authInfo=None):
        """
            authenticats with OpenStack API's (through keystone)

            Parameters:
                        authInfo: Object that holds information to authenticate with keystone.
                        If none, this requires the [machine] user to be stated as an OpenStack admin (admin-openrc.sh file)
                        It will look for environment variables holding informations to authenticate.
                        see docs.openstack.org/liberty/install-guide-ubuntu/keystone-openrc.html
        """
        if authInfo is None:
            authInfo = {
                'auth_url': env['OS_AUTH_URL'],
                'username': env['OS_USERNAME'],
                'password': env['OS_PASSWORD'],
                'project_name': env['OS_PROJECT_NAME'],
                'user_domain_name': env['OS_USER_DOMAIN_NAME'],
                'project_domain_name': env['OS_PROJECT_DOMAIN_NAME']
            }
        return keystoneSession.Session(auth=v3.Password(**authInfo))

    def createImage(self, imageInfo=None):
        """
            Creates a glance image following imageInfo.

            Parameters:
                        imageInfo (<OsImage> see os_image.py)

            Returns:
                        Glance image object
        """
        if not isinstance(imageInfo, OsImage):
            return None
        image = self.glance.images.create(name=imageInfo.image_name,
            container_format=imageInfo.image_container,
            disk_format=imageInfo.image_format)
        self.glance.images.upload(image.id, open(imageInfo.file_path,'rb'))
        return image

    def deleteImage(self, imageRef):
        """
            Deletes image 'imageRef'.
            Uses glance API

            Parameters:
                        imageRef: Glance Image Object

        """
        return self.glance.images.delete(imageRef.id)

    def createInstance(self, instanceName, glanceImage, flavorName='m1.small', networkId=None, computeType=False):
        """
            Creates an instance.
            If computeType == True, it returns an instance of openstack compute.
            If computeType == False, it returns an instance of nova server.

            Parameters:
                        instanceName (string): The name of the instance
                        glanceImage (openstack glance image object): the image to be used for the instance server
                        flavorName (string): An OpenStack instance flavor
                        networkId (openstack network uuid): the uuid used for the network
                        computeType (boolean): Flag that changes the way how the instance is created (through nova api or compute)
            Returns:
                        The instance server
        """
        if networkId is None:
            networkId = 'none'
        novaFlavor = self.nova.flavors.find(name=flavorName)

        if computeType:
            return self.openstackConn.compute.create_server(name=instanceName, image_id=glanceImage.id, flavor_id=novaFlavor.id, networks=[{'uuid': networkId}])
        else:
            return self.nova.servers.create(instanceName, glanceImage, novaFlavor, nics=[{'net-id': networkId}])

    # Workaround, since documentation doesn't provide enough information about a get operation by image name
    # @TODO: Refactor ASAP
    # Serious performance issue
    def getImageByName(self, name):
        """
            Gets the glance image by name
        """
        imageList = self.glance.images.list()
        filteredImageList = list(filter(lambda image: image.name == name, imageList))
        if len(filteredImageList) == 0 :
            return None
        return filteredImageList[0]

    def networkSetup(self, name):
        """
            Creates a default network configuration and returns the network uuid
        """
        network = self.neutron.list_networks(name=name)

        if len(network['networks']) > 0:
            networkId = network['networks'][0]['id']
        else:
            # https://developer.openstack.org/api-ref/network/v2/#create-network
            networkRequest = {
                'network': {
                    'name': name,
                    'admin_state_up': True
                }
            }

            response = self.neutron.create_network(networkRequest)
            networkId = response['network']['id']

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
        return networkId
