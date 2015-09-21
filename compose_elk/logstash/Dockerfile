FROM logstash:latest

RUN apt-get update \
    && apt-get install -y gcc make libtool tcpdump snmp \
    && rm -rf /var/lib/apt/lists/* \
    && wget http://www.inmon.com/bin/sflowtool-3.22.tar.gz \
    && tar xzf sflowtool-3.22.tar.gz \
    && rm sflowtool-3.22.tar.gz \
    && cd sflowtool-3.22 \
    && ./configure \
    && make \
    && make install \
    #&& wget https://github.com/logstash-plugins/logstash-codec-netflow/archive/master.zip \
    #&& unzip master.zip \
    # && rm master.zip \
    # && cd logstash-codec-netflow-master \
    && bundle install \
    && plugin install logstash-filter-translate \
                      logstash-filter-geoip \
                      logstash-filter-dns \
                      logstash-codec-rubydebug \
                      logstash-codec-netflow 
