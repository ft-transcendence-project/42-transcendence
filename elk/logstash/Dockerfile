ARG STACK_VERSION
FROM docker.elastic.co/logstash/logstash:${STACK_VERSION}
COPY logstash.conf /usr/share/logstash/pipeline/logstash.conf
COPY ilm-policy.json /usr/share/logstash/config/ilm-policy.json
COPY --chmod=0755 create_index_pattern.sh /usr/local/bin/create_index_pattern.sh
COPY --chmod=0755 set_ilm_policy.sh /usr/local/bin/set_ilm_policy.sh