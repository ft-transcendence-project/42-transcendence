#!/bin/bash

KIBANA_HOST="https://kibana:5601"
KIBANA_USER="elastic"
KIBANA_PASS=${KIBANA_PASSWORD}
INDEX_PATTERN_NAME="Logstash data view"
INDEX_PATTERN_TITLE="logstash-*"

cat <<EOF > index-pattern.json
{
  "data_view": {
    "name": "${INDEX_PATTERN_NAME}",
    "title": "${INDEX_PATTERN_TITLE}",
    "timeFieldName": "@timestamp",
    "fields": {
      "tags": {
        "name": "tags",
        "type": "keyword",
        "aggregatable": true
      },
      "message_type": {
        "name": "message_type",
        "type": "keyword",
        "aggregatable": true
      },
      "level": {
        "name": "level",
        "type": "keyword",
        "aggregatable": true
      }
    }
  }
}
EOF

curl -X POST "${KIBANA_HOST}/api/data_views/data_view" \
  --cacert /usr/share/logstash/config/certs/ca/ca.crt \
  -H "kbn-xsrf: string" \
  -H "Content-Type: application/json" \
  -u ${KIBANA_USER}:${KIBANA_PASS} \
  --data @index-pattern.json

rm index-pattern.json
