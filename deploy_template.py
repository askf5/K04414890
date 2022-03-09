#!/usr/bin/env python

from onboard2 import OnboardDSC
from getpass import getpass
from pprint import pprint
import argparse

#Gather device information from CLI args
parser = argparse.ArgumentParser()
parser.add_argument("-m1", "--mgmt1", 
    help="Mgmt IP addr of 1st device", required=True)
parser.add_argument("-m2", "--mgmt2", 
    help="Mgmt IP addr of 2nd device", required=True)
parser.add_argument("-i1", "--internal1", 
    help="Internal self IP addr of 1st device", required=True)
parser.add_argument("-i2", "--internal2", 
    help="Internal self IP addr of 2nd device", required=True)
parser.add_argument("-e1", "--external1", 
    help="External self IP addr of 1st device", required=True)
parser.add_argument("-e2", "--external2", 
    help="External self IP addr of 2nd device", required=True)
parser.add_argument("-p", "--password", 
    help="Activates hidden password prompt", action='store_true', required=True)
args = parser.parse_args()

#Gather pw as user input for security
if args.password:
    pw = getpass("Enter your BIG-IP admin password: ")
    pw2 = getpass("Enter your BIG-IP 2 admin password: ")

#Assign variables
mgmt_ip_1 = args.mgmt1
mgmt_ip_2 = args.mgmt2
int_self_ip_1 = args.internal1
int_self_ip_2 = args.internal2
ext_self_ip_1 = args.external1
ext_self_ip_2 = args.external2

'''Create object then run function to onboard 1st half of DSC/VLAN set up 
on 1st device.'''
d1 = OnboardDSC(mgmt_ip_1, mgmt_ip_1, mgmt_ip_2, int_self_ip_1, 
    ext_self_ip_1, pw)
d1.RunAllOnboard()

'''If deployment on 1st device was successful, (an f5sdk exception should occur
if not) create another object then run function to onboard and 2nd half 
of DSC/VLAN set up on 2nd device. The mgmt_ip_2 is now used for DO target device
and int and ext self_ip_2 are primary self ips for this object instance'''

d2 = OnboardDSC(mgmt_ip_2, mgmt_ip_1, mgmt_ip_2, int_self_ip_2, 
    ext_self_ip_2, pw2)
d2.RunAllOnboard()

#Validate that configuration has been deployed as expected
print("\n-----New configuration:-----\n")
#Only need to see dsc config from perspective of one device, the d2 object 
pprint(d2.dsc_ip)
pprint(d2.device_group)
pprint(d2.device_trust)
#Vlans and selfips
pprint(d1.vlans)
pprint(d1.selfips)
pprint(d2.vlans)
pprint(d2.selfips)

#Print the result returned from DO service on BIG-IP
print("\n-----DO deployment result:-----\n")
pprint(d1.create['result'], width=60)
pprint(d2.create['result'], width=60)
