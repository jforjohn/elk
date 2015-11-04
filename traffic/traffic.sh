#!/bin/bash

#IP_LOGSTASH=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' logstash`
IP_LOGSTASH=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' indexing`
PORT_LOGSTASH=6343
SAMPLING=1024
POLLING=1024
#PCAP_FILE="smia.pcap"
#PCAP_FILE="EXPLOIT_Apple_iPhone_1.1.2_Remote_Denial_of_Service_Exploit_EvilFingers.pcap"
PCAP_FILE="http.pcap"

sudo docker rm -f ovs tcpreplay
sudo rm -rf sudo /var/run/netns/

docker run -itd --name ovs --cap-add NET_ADMIN --cap-add SYS_MODULE -v /lib/modules:/lib/modules socketplane/openvswitch

#docker run -itd --name tcpreplay --net=none -v ~/elk/traffic/tcpreplay/pcapfiles:/home/ jaysot/tcpreplay
docker run -itd --name tcpreplay -v ~/elk/traffic/tcpreplay/pcapfiles:/home/ jaysot/tcpreplay

sh ~/elk/traffic/p2pconnection.sh

docker exec ovs modprobe openvswitch  
docker exec ovs supervisorctl restart ovs-vswitchd
docker exec ovs ovs-vsctl add-br br0 
docker exec ovs ovs-vsctl add-port br0 veth_ovs 
docker exec ovs ovs-vsctl -- --id=@sflow create sflow agent=eth0 target=\"$IP_LOGSTASH:$PORT_LOGSTASH\" header=128 sampling=$SAMPLING polling=$POLLING -- set bridge br0 sflow=@sflow
#docker exec ovs ovs-vsctl -- set Bridge br0 netflow=@nf --   --id=@nf create   NetFlow   targets=\"$IP_LOGSTASH:$PORT_LOGSTASH\" active-timeout=10

docker exec tcpreplay tcpreplay --topspeed --intf1=veth_tcpr /home/$PCAP_FILE
#docker exec tcpreplay tcpreplay --topspeed --intf1=eth0 /home/$PCAP_FILE
