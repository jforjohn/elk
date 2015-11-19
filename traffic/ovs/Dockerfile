#FROM socketplane/openvswitch
FROM mgkwill/openvswitch

RUN apt-get update \
    && apt-get install tcpdump
    && rm -rf /var/lib/apt/lists/* 
