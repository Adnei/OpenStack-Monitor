#!/bin/bash
. /root/setup/admin-openrc-newcli.sh;
rm -rf *.pcap;
rm -rf *.log;
rm -rf *.db;

#TODO Iterate over a list of images... Maybe pass images as arguments to clean.sh
openstack server delete instanceServer;
openstack image delete fedora31;

#shows if there are dumps stuck
ps aux | grep tcpdump
#TODO To kill any stuck tcpdump
