#!/bin/bash
# TODO --> CREATE A MAKE FILE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#It will be a pip required
git clone https://github.com/Adnei/service_identifier.git;
apt -y install python3-tk python3-pip && source /root/setup/admin-openrc-newcli.sh;
pip3 install -r .required;
#TODO: wget should read a list of images
#wget https://download.fedoraproject.org/pub/fedora/linux/releases/31/Cloud/x86_64/images/Fedora-Cloud-Base-31-1.9.x86_64.qcow2; # 319MB
wget https://cdimage.debian.org/cdimage/openstack/current-10/debian-10-openstack-amd64.raw; # 2GB
wget https://cdimage.debian.org/cdimage/openstack/current-10/debian-10-openstack-amd64.qcow2; # 550MB
#wget https://cloud-images.ubuntu.com/bionic/current/bionic-server-cloudimg-amd64.img; # 329MB
#wget https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img; # 519MB
#wget https://download.cirros-cloud.net/0.4.0/cirros-0.4.0-aarch64-disk.img; # 15MB
wget http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud-1707.qcow2; # 1.3 GB
wget http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2; #898 MB
wget https://download.fedoraproject.org/pub/fedora/linux/releases/32/Cloud/x86_64/images/Fedora-Cloud-Base-32-1.6.x86_64.qcow2 #289MB
wget https://download.freebsd.org/ftp/releases/VM-IMAGES/12.0-RELEASE/amd64/Latest/FreeBSD-12.0-RELEASE-amd64.qcow2.xz #454MB


source /root/setup/info.mgmt

VLAN=${MGMT_NETWORK_INTERFACE}
echo "VLAN=${MGMT_NETWORK_INTERFACE}"
