#!/bin/bash
# use local routes for everything except AWS
# Skip ipv6 routes
#
#This asssumes a linux host
if [[ $UID -ne 0 ]]
then
    echo "Must be root"
    exit 1
fi

localroute(){
    prefix=$1
    if [[ "$prefix" =~ "/32" ]]; then
        route add -host $prefix dev tun0
    else
        route add -net $prefix dev tun0
    fi
}

AWS_US_ONLY(){
    #now we add all the individual routes
    #Since the table is too big just limit us to us addresses
    curl -s https://ip-ranges.amazonaws.com/ip-ranges.json \
        | jq -r '.prefixes[]|select(.region?|match("us-"))|.ip_prefix' \
        | while read prefix ; do
            localroute $prefix 2>&1 | grep -v "File exists"
          done
}

AWS_US_ONLY
