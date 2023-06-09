#!/bin/sh

found=$(which sshuttle)
if [ $? -ne 0 ]
then
    echo "Please install sshuttle"
    echo "apt-get install sshuttle or brew install shuttle or whatever"
    exit 1
fi

echo grabbing Nodes IP range
ipnodes="$(kubectl get nodes | grep -v NAME | sed -e 's/.us-[we][ea]st.*//g' | cut -f2,3 -d- | sort | uniq | sed -e 's/-/./g').0.0/16"
echo Nodes IP range:  $ipnodes

echo grabbing services IP range
ipservices="$(kubectl get services | awk '{print $3}' | grep -v CLUSTER | grep -v [Nn]one | cut -f1,2 -d. | uniq).0.0/16"
echo Services IP range:  $ipservices

echo grabbing DNS host
dnshost=$(kubectl -n kube-system get service kube-dns | awk '{print $3}' | grep -v CLUSTER)
echo DNS service: $dnshost

echo spawning kuttle-${USER} If it errors with "already exists" it is fine
kubectl run kuttle-${USER} --image=alpine:latest --restart=Never -- sh -c 'apk add python3 --update && exec tail -f /dev/null'

#Enable this for laptops with dnsmasq ( most of them)
DNSMASQ="--dns --ns-hosts=127.0.0.1 --to-ns=$dnshost"
# Uncomment to disable
#DNSMASQ=""

echo starting sshutle, you wil need a SUDO password
sshuttle -r kuttle-${USER} -e kuttle $DNSMASQ $ipnodes $ipservices
