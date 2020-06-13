#!/bin/bash
# TODO --> CREATE A MAKE FILE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

. /root/setup/admin-openrc-newcli.sh;
rm -rf *.pcap;
rm -rf *.log;
rm -rf *.db;
rm -rf lsof*;
rm -rf /proj/labp2d-PG0/temp_lsof;

#TODO Iterate over a list of images... Maybe pass images as arguments to clean.sh
openstack server delete instanceServer;
openstack image delete fedora31;

#shows if there are dumps stuck
ps aux | grep tcpdump
#TODO To kill any stuck tcpdump
