#!/bin/bash

rm -rf *.pcap;
rm -rf *.log;
rm -rf *.db;
#shows if there are dumps stuck 
ps aux | grep tcpdump
