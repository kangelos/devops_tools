#!/usr/bin/python3
import datetime
from elasticsearch import Elasticsearch
import os

'''
export apache like logs from elasticsearch traefik data
Angelos Karageorgiou angelos@unix.gr
Disclaimer: No GPT was used ;-)
'''

#Please edit
ELASTIC_USER="elastic"
ELASTIC_PASSWORD=os.getenv('ELASTIC_PASSWORD')
ELASTIC_HOST=os.getenv('ELASTIC_HOST')

# make this tighter or face timeouts
INDEX_PATTERN="*"
SCROLL="1m" #increase if above is too inclusive

DAYS_BEHIND=90

today = datetime.datetime.now()
diffdate = datetime.timedelta(days = DAYS_BEHIND)
past = (today - diffdate).strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]

# Thank you mdme kibana
query= {
    "bool": {
      "must": [],
      "filter": [
        {
          "bool": {
            "should": [
              {
                "match": {
                  "kubernetes.labels.app_kubernetes_io/name": "traefik"
                }
              }
            ],
            "minimum_should_match": 1
          }
        },
        {
          "range": {
            "@timestamp": {
              "format": "strict_date_optional_time",
              "gte": past,
              "lte": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]
            }
          }
        }
      ],
    }
  }

es = Elasticsearch(ELASTIC_HOST, http_auth=(ELASTIC_USER, ELASTIC_PASSWORD))
res = es.search(index=INDEX_PATTERN, query=query, size=10000, scroll=SCROLL)
scroll_id=res['_scroll_id']

while scroll_id:
    for hit in res['hits']['hits']:
        print(hit['_source']['message'])
    res = es.scroll(
        scroll_id = scroll_id,
        scroll = SCROLL # time value for search, does it even matter?
    )
    scroll_id=res['_scroll_id']
