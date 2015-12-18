#!/bin/bash

service rsyslog start
salt-minion --daemon --log-level debug
echo "Going into infinity"
sleep infinity;true
