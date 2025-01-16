#!/bin/bash

ELASTIC_HOST="https://es01:9200"
KIBANA_USER="elastic"
KIBANA_PASS=${KIBANA_PASSWORD}

# Create index template
curl -X PUT "${ELASTIC_HOST}/_template/logstash" \
  --cacert /usr/share/logstash/config/certs/ca/ca.crt \
  -H "Content-Type: application/json" \
  -u ${KIBANA_USER}:${KIBANA_PASSWORD} \
  -d @/usr/share/logstash/config/logstash-template.json
