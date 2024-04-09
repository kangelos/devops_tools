#!/bin/bash
#
# script to convert otterize output to k8s network policies
context=$(kubectl config current-context)
[ -f /tmp/${context}.map ]  || (otterize network-mapper list > /tmp/${context}.map)
while read line
do
  # beginning of a section 
  found=$(echo "$line" | grep 'calls:$')
  if [[ $? -eq 0 ]]
  then
    source=$(echo $line | awk '{print $1}')
    source_namespace=$(echo $line | awk '{print $4}')
    continue
  else
    # the service that is called
    dest=$(echo $line | awk '{print $2}')
    dest_namespace=$(echo $line | awk '{print $5}')
  fi
  echo "---"
  echo "#$source ($source_namespace) --> $dest ($dest_namespace)"
  cat << EOF
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: ${dest}-ingress
  namespace: $dest_namespace
spec:
  podSelector:
    matchLabels:
      name: ${dest}
  policyTypes:
  - Ingress
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: ${source_namespace}
      - podSelector:
          matchLabels:
            name: $source
EOF
done < /tmp/${context}.map
