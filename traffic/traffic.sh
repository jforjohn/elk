#!/bin/bash

IP_LOGSTASH=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' logstash`
PORT_LOGSTASH=6543

sudo docker rm -f ovs tcpreplay
sudo rm -rf sudo /var/run/netns/

docker run -itd --name ovs --cap-add NET_ADMIN --cap-add SYS_MODULE -v /lib/modules:/lib/modules --link logstash socketplane/openvswitch

docker run -itd --name tcpreplay --net=none -v ~/elk/traffic/tcpreplay/pcapfiles:/root/ jaysot/tcpreplay

sh ~/elk/traffic/p2pconnection.sh

docker exec ovs modprobe openvswitch  
docker exec ovs supervisorctl restart ovs-vswitchd
docker exec ovs ovs-vsctl add-br br0 
docker exec ovs ovs-vsctl add-port br0 veth_ovs 
docker exec ovs ovs-vsctl -- --id=@sflow create sflow agent=eth0 target=\"$IP_LOGSTASH:$PORT_LOGSTASH\" header=128 sampling=64 polling=10 -- set bridge br0 sflow=@sflow

#docker exec tcpreplay tcpreplay --intf1=veth_tcpr /root/smia.pcap
