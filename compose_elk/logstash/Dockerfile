FROM logstash:latest

RUN apt-get update \
    && apt-get install -y gcc make libtool tcpdump \
    && rm -rf /var/lib/apt/lists/* \
    && wget http://www.inmon.com/bin/sflowtool-3.22.tar.gz \
    && tar xzf sflowtool-3.22.tar.gz \
    && rm sflowtool-3.22.tar.gz \
    && cd sflowtool-3.22 \
    && ./configure \
    && make \
    && make install \
    && plugin install logstash-filter-translate
