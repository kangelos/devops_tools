#!/bin/bash
#
#Create the treafik index

year=$(date +%Y)
mon=$(date +%m)
day=$(date +%d)
curl  -s -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
      -XPOST "${ELASTIC}/_reindex?wait_for_completion=false" \
      -H 'Content-Type: application/json' -d "{
          \"conflicts\": \"proceed\",
          \"source\": {
            \"index\": \"SOURCE-${year}.$mon.$num\"
          },
          \"dest\": {
            \"index\": \"traefik-ingested-${year}.$mon.$num\",\"pipeline\": \"traefik-ingestor\" }
        }"
