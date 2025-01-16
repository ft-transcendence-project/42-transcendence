#!/bin/bash

KIBANA_HOST="https://kibana:5601"
KIBANA_USER="elastic"
KIBANA_PASS=${KIBANA_PASSWORD}

curl -X POST "${KIBANA_HOST}/api/data_views/data_view" \
  --cacert /usr/share/logstash/config/certs/ca/ca.crt \
  -H "kbn-xsrf: string" \
  -H "Content-Type: application/json" \
  -u ${KIBANA_USER}:${KIBANA_PASS} \
  --data @/usr/share/logstash/config/data-view.json
