'''
idea from https://gist.github.com/psa-jforestier/2fd390ac9cc6d1bef7073156893f84d7
import WAF logs from S3 to elastic
Angelos Karageorgiou
'''
import json
import urllib.parse
import tempfile
import os
import socket
import subprocess
import gzip
import datetime
import logging
import re
import ssl
import urllib3
import boto3
import urllib.request

BATCH = 100
URL = 'https://yourelasticurl'
Headers = {
        'Content-type':  'application/json',
        'Accept':        '*/*',
        'Authorization': 'Basic figurer_that_out_for_yourself'
        }

def stream_to_elk(lines, s3bucket):
    """
    Receive an event and post it to elastic
    index is the bucket name ...
    """
    http = urllib3.PoolManager(cert_reqs = ssl.CERT_NONE)
    urllib3.disable_warnings()
    index = s3bucket+ "-" + datetime.datetime.utcnow().strftime("%Y.%m.%d")
    mydata="\n".join(["{ \"index\": {} }\n"+str(entry) for entry in lines])+"\n"
    response = http.request('POST', URL+"/"+index+"/_bulk",
                             headers=Headers,
                             body=mydata.encode('UTF-8')
                             )
    return json.loads(response.data)
    

def lambda_handler(event, context):
    for record in event['Records']:
        s3info = record['s3']
        s3bucket = s3info['bucket']['name']
        s3objectkey = urllib.parse.unquote(s3info['object']['key'])
        s3objectsize = s3info['object']['size']

        print(" Bucket : " + s3bucket)
        print("    key : " + s3objectkey)
        print("   size : " + str(s3objectsize))

        s3 = boto3.resource('s3', region_name='us-west-2')
        bucket = s3.Bucket(s3bucket)
        object = bucket.Object(s3objectkey)
        response = object.get()
        bindata = response['Body'].read()
        text_data=gzip.decompress(bindata).decode("utf-8")
        
        events = []
        i = 0
        for line in text_data.split("\n"):
            i = i + 1
            events.append(line)
            if i % BATCH == 0:
                print("Sending events %d " % i)
                response = stream_to_elk(events, s3bucket)
                events = []
        if len(events) > 0:
            stream_to_elk(events, s3bucket)
        print("Sent %d events from this object" % i)

    return True

