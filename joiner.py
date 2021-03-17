#!/usr/bin/python3

"""
Convert multiline logs from s3 into digestible ES docs
A new line starts with a timestamp , subsequent lines do not

make sure you create this index
 I did it from a batch script 
curl --silent --user "$ES_USER:$ES_PASS" \
     --header "Content-Type: application/json" \
    -X PUT  -d @index.json     ${ES_URL}/logs

index={
   "mappings": {
       "properties": {
         "date": {
        	"type": "date",
		      "format": "strict_date_optional_time"
         },
         "application": {
               "type": "text"
         },
         "pod": {
               "type": "text"
         },
         "message": {
               "type": "text"
         }
       }
   }
 }  

"""

import sys
import re
import os
from elasticsearch import Elasticsearch, ElasticsearchException, helpers

LINESTART="^\d{4,4}-\d{2,2}-\d{2,2}\s\d{2,2}:\d{2,2}:\d{2,2}[\.,]\d{3,4}"

es = Elasticsearch([os.getenv('ES_URL')], http_auth=(os.getenv('ES_USER'), os.getenv('ES_PASS'))) # reconnect


DEBUG=False
VERBOSE=True
count=0
BULKCOUNT=500


def jsonline(pod,app,date,message):
    """
    convert a log line into a json line ES digestible doc
    """
    message = re.sub('^\s*','',message) # no spaces
    message = re.sub('\s*$','',message)
    # sometimes this line works best
#    message=message.replace('\\',r'\\\\').replace('"', r'\"').replace('\n', r'\n').replace("\t",r'\t').replace("\'", r'\'')
    # othertimes this line works best
    message=message.replace('\\',r'\\\\').replace('"', r'\"').replace('\n', r'\n').replace("\t",r'\t')
    date=date.replace(",",".").replace(" ","T") # ES digestible date
    data=("{"
            "\"date\": \"%s\" ,"
            "\"application\": \"%s\" , "
            "\"pod\": \"%s\", "
            "\"message\": \"%s\" "
            "}") % (date, app, pod, message)
    return(data)


def bulkpost(centiline):
    """
    Bulk upload 
    """
    es_entries = []
    for doc in centiline:
        entry = {"_index": "logs",
                "_type": "_doc",
                "_source": doc }
        es_entries.append(entry)
    try:
        response=helpers.bulk(es, es_entries, refresh=True, request_timeout=60)  
        if DEBUG:
            print ("\nRESPONSE:", response)  # if all is well is should print the number of documents ingested
    except Exception as e:
        print("\nERROR:", e)
    if VERBOSE:
        print("Documents:%d\r" % count, end="")


if __name__ == '__main__':
    """
    Keep reading one line at a time and appending to completeline
    if a line starts with a timestamp process the "completeline"
    """
    try:
        (env,pod,app)=sys.argv[1].split('.')
    except:
        print("which pod")
        exit(1)

    f = sys.stdin
    line=f.readline()
    completeline=line
    centiline=[]
    while line:
        count += 1
        line=line.rstrip()
        match=re.match(LINESTART,line)
        if match:    # gotta be a new date time --- and have gone through the loop once
            prematch=re.match(LINESTART,completeline)   # pick up the previous date
            if prematch:
                if DEBUG:
                    print("\nline %s" % line)
                    print("match %s" % match.group())
                    print("prematch %s" % prematch.group())
                    print("completeline %s" %completeline)
                completeline = completeline.replace(prematch.group(),"")    # tiny cleanup
                centiline+=[jsonline(pod,app,prematch.group(),completeline)] # list of complete log entries
            else:
                print("Weird, completeline has no date: %s" % completeline)
            completeline=line
            if count % BULKCOUNT == 0:
                bulkpost(centiline)
                centiline=[]
        else:
            completeline = completeline +" "+line # avoid joins with new lines

        line=f.readline()   # keep reading

    print("Documents:%d" % count) # last output
    if centiline != []: # send any left overs
        bulkpost(centiline)
