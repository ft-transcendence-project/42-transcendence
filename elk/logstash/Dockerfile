ARG STACK_VERSION
FROM docker.elastic.co/logstash/logstash:${STACK_VERSION}
COPY logstash.conf /usr/share/logstash/pipeline/logstash.conf
COPY data-view/data-view.json /usr/share/logstash/config/data-view.json
COPY ilm-policy/logstash-ilm-policy.json /usr/share/logstash/config/logstash-ilm-policy.json
COPY --chmod=0755 data-view/create_data_view.sh /usr/local/bin/create_data_view.sh
COPY --chmod=0755 ilm-policy/set_ilm_policy.sh /usr/local/bin/set_ilm_policy.sh