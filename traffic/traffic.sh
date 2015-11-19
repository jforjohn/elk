#!/bin/bash

#IP_LOGSTASH=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' logstash`

PORT_COLLECTOR=6343
SAMPLING_1=8
SAMPLING_2=64
POLLING=1024
#PCAP_FILE="smia.pcap"
#PCAP_FILE="EXPLOIT_Apple_iPhone_1.1.2_Remote_Denial_of_Service_Exploit_EvilFingers.pcap"
PCAP_FILE_1="http.pcap"
#PCAP_FILE_1="smia.pcap"
#PCAP_FILE_2="slowdownload.pcap"

sudo docker rm -vf ovs1 tcpreplay1 indexing1 ovs2 tcpreplay2 indexing2
sudo rm -rf sudo /var/run/netns/

#docker run -itd --name indexing1 --link elasticsearch:elasticsearch -v ~/elk/index_elk/:/root/ jaysot/index_elasticsearch python /root/sflowIndexing.py sflow-1

#docker run -itd --name indexing2 --link elasticsearch:elasticsearch -v ~/elk/index_elk/:/root/ jaysot/index_elasticsearch python /root/sflowIndexing.py sflow-2

IP_COLLECTOR_1=172.17.42.1
#IP_COLLECTOR_1=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' indexing1`
#IP_COLLECTOR_2=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' indexing2`

docker run -itd --name ovs1 --cap-add NET_ADMIN --cap-add SYS_MODULE -v /lib/modules:/lib/modules socketplane/openvswitch

#docker run -itd --name ovs2 --cap-add NET_ADMIN --cap-add SYS_MODULE -v /lib/modules:/lib/modules socketplane/openvswitch

#docker run -itd --name tcpreplay --net=none -v ~/elk/traffic/tcpreplay/pcapfiles:/home/ jaysot/tcpreplay
docker run -itd --name tcpreplay1 -v ~/elk/traffic/tcpreplay/pcapfiles:/home/ jaysot/tcpreplay

#docker run -itd --name tcpreplay2 -v ~/elk/traffic/tcpreplay/pcapfiles:/home/ jaysot/tcpreplay


sh ~/elk/traffic/p2pconnection.sh ovs1 tcpreplay1
#sh ~/elk/traffic/p2pconnection.sh ovs2 tcpreplay2

docker exec ovs1 modprobe openvswitch  
docker exec ovs1 supervisorctl restart ovs-vswitchd
docker exec ovs1 ovs-vsctl add-br br0 
docker exec ovs1 ovs-vsctl add-port br0 veth_ovs 
docker exec ovs1 ovs-vsctl -- --id=@sflow create sflow agent=eth0 target=\"$IP_COLLECTOR_1:$PORT_COLLECTOR\" header=128 sampling=$SAMPLING_1 polling=$POLLING -- set bridge br0 sflow=@sflow
#docker exec ovs1 ovs-vsctl -- set Bridge br0 netflow=@nf --   --id=@nf create   NetFlow   targets=\"$IP_COLLECTOR_1:$PORT_COLLECTOR\" active-timeout=10

docker exec tcpreplay1 tcpreplay --mbps=10.0 --intf1=veth_tcpr /home/$PCAP_FILE_1

#docker exec ovs2 modprobe openvswitch  
#docker exec ovs2 supervisorctl restart ovs-vswitchd
#docker exec ovs2 ovs-vsctl add-br br0 
#docker exec ovs2 ovs-vsctl add-port br0 veth_ovs 
#docker exec ovs2 ovs-vsctl -- --id=@sflow create sflow agent=eth0 target=\"$IP_COLLECTOR_2:$PORT_COLLECTOR\" header=128 sampling=$SAMPLING_2 polling=$POLLING -- set bridge br0 sflow=@sflow
#docker exec ovs ovs-vsctl -- set Bridge br0 netflow=@nf --   --id=@nf create   NetFlow   targets=\"$IP_COLLECTOR_2:$PORT_COLLECTOR\" active-timeout=10

#docker exec -d tcpreplay2 tcpreplay --topspeed --intf1=veth_tcpr /home/$PCAP_FILE_2
