ARG STACK_VERSION
FROM docker.elastic.co/logstash/logstash:${STACK_VERSION}
COPY logstash.conf /usr/share/logstash/pipeline/logstash.conf
COPY --chmod=0755 create_index_pattern.sh /usr/local/bin/create_index_pattern.sh