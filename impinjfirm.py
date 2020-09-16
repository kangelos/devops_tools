#!/usr/bin/env python3
# find the firmware on all rfid readers
# Angelos Karageorgiou angelos@unix.gr
# pip3 install pexpect


import os
import sys
import pexpect



def getfirmware(ip,user,password):
    """
    use expect to send command to an impinj reader
    """
    child = pexpect.spawn("ssh %s@%s" % (user,ip) )
    # uncomment for debugging purposes
    # child.logfile = sys.stdout.buffer

    child.expect('.*password: ')
    child.sendline(password)
    child.expect('> ')
    child.sendline('show image summary')
    c=child.readline()
    while len(c) > 0:
        arr = c.decode("utf-8").split("=")
        if arr[0]:
            if arr[0] == "PrimaryImageSystemVersion":
                return(arr[1])
        c=child.readline()
    child.expect('> ')
    child.sendline('exit')


print("Firmware Version %s" % getfirmware('192.168.220.10','root',password))
