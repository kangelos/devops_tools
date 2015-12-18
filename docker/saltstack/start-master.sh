#!/bin/bash

service rsyslog start
service salt-minion start
service salt-master start
service sshd start
echo "Sleeping a bit: 15 secs"
sleep 15
Echo "Auto-accepting All minion keys"
salt-key -A -y
echo "Going into infinity"
sleep infinity;true
