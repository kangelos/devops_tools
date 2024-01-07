#!/bin/bash
#
# script to convert otterize output to mermaid and then svg
#
# you need the mermaid cli
# sudo npm install -g @mermaid-js/mermaid-cli 
# sudo apt install puppeteer chromium-browser
TOSKIP="^toskip.*"
namespace=$(kubectl config view --minify -o jsonpath='{..namespace}')

(
#echo "flowchart TD"
echo "flowchart LR"
otterize -n $namespace network-mapper list | while read line
do
  # beginning of a section 
  found=$(echo "$line" | grep 'calls:$')
  if [[ $? -eq 0 ]]
  then
    source=$(echo $line | sed -e "s/ in namespace $namespace calls://g")
    continue
  else
    # the service that is called
    dest=$(echo $line | sed -e 's/^-//g' -e "s/ in namespace $namespace//g")
  fi
  echo "$source --> $dest" | grep -v $TOSKIP
done
) > /tmp/$namespace.maid

# generate the svg now
mmdc -i /tmp/$namespace.maid -o /tmp/$namespace.svg
ls /tmp/$namespace*

#optional, reset connection data
#otterize network-mapper reset
