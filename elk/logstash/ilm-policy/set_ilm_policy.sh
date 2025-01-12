#!/bin/bash

ELASTIC_HOST="https://es01:9200"
KIBANA_USER="elastic"
KIBANA_PASS=${KIBANA_PASSWORD}

# ILMポリシーの適用
curl -X PUT "${ELASTIC_HOST}/_ilm/policy/logstash-logs-policy" \
  -H "Content-Type: application/json" \
  --cacert /usr/share/logstash/config/certs/ca/ca.crt \
  -u ${KIBANA_USER}:${KIBANA_PASSWORD} \
  -d @/usr/share/logstash/config/logstash-ilm-policy.json
