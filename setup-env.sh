#!/bin/bash

apt -y install python3-tk python3-pip && source /root/setup/admin-openrc-newcli.sh;
pip3 install -r .required;
#TODO: wget should read a list of images
wget https://download.fedoraproject.org/pub/fedora/linux/releases/31/Cloud/x86_64/images/Fedora-Cloud-Base-31-1.9.x86_64.qcow2;

#TODO script to find out administrative vlan
