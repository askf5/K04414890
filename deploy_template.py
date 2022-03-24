#!/usr/bin/env python

from onboard import OnboardDSC
from getpass import getpass
import sys

#Loop through key value args and add them to dict
#Dict passed to template renderer in module
do_data = {}
for i in sys.argv[3:]:
    args = i.split("=")
    do_data.update({args[0]: args[1]})

#Assign variables from pos args and prompt
do_target_ip = sys.argv[1]
do_template = sys.argv[2]
pw = getpass("Enter your BIG-IP admin password: ")

#Look for update key value. If not defined, set update to empty.
try:
    update = do_data['update']
except:
    update = ''

'''Create object then run function to onboard'''
d = OnboardDSC(do_target_ip, do_template, do_data, pw, update)
d.RunAllOnboard()
