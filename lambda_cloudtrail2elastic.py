"""
python lambda function to post events to any elastic stack
angelos Nov 21
create the lambda function cloudtrail2elastic 
Go to your cloudtrail and send the logs to cloudwatch
switch to cloudwatch and create a subscription from these log groups to the above lambda function
"""
import json
import datetime
import urllib3
import sys
import gzip
import base64

index = "cloudtrail-" + datetime.datetime.utcnow().strftime("%Y.%m.%d")

Headers = {'Content-type': 'application/json',
        'Accept': '*/*',
        'Authorization': 'Basic base64user:pass'   
         }

http = urllib3.PoolManager()

def lambda_handler(event, context):
    """
    Receive an event and post it to elastic
    """
    data=event["awslogs"]["data"]
    bindata=base64.b64decode(data)
    content=gzip.decompress(bindata)
    mydict=json.loads(content.decode('UTF-8'))
    for entry in mydict["logEvents"]:
        response = http.request('POST', "https://elastic.blahblah/"+index+"/_doc/",
                                 headers=Headers,
                                 body=entry["message"].encode('UTF-8') )
