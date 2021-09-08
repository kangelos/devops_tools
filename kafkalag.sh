#!/bin/bash

# 
# Drill down into your confluent kafka cluster 
# find consumer groups
# find problematic pods
# and get their logs
# angelos@unix.gr

KBASH="kubectl exec -ti kafkaclient -- bash"
server=$(kubectl get services | grep 'kafkaconfluent-.*cp-kafka.*9092' | grep -v headless  | awk '{print $1}')
CMD="bin/kafka-consumer-groups.sh --bootstrap-server $server:9092 --describe --group $1|sort -n -k5"

if [ "$1" == "" ]
then
  echo "Please use kafkalag.sh <CONSUMER_GROUP>"
  echo "Consumer groups list:"  
  $KBASH -c "bin/kafka-consumer-groups.sh --bootstrap-server $server:9092 --list"
  exit
fi
#overall picture
$KBASH -c "$CMD"

echo "===================="
echo "Biggest lag is from:"
lagger=$($KBASH -c "$CMD" | tail -n 1 | awk '{print $7}' | sed -e 's/\///')

lagline=$(kubectl get pods -o wide |grep $lagger)
echo $lagline
echo "===================="
if [ "$2" == "-l" ]
then
  pod=$(echo $lagline | awk '{print $1}')
  echo "logs -f $pod"
  kubectl logs -f $pod
else
  echo "use kafkalag.sh $1 -l to go directly to the pod's logs"
fi

