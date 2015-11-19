#!/bin/bash
# Learn the container process IDs
# and create their namespace entries
sudo mkdir -p /var/run/netns
OVS_PID=`docker inspect -f '{{.State.Pid}}' $1`
TCPR_PID=`docker inspect -f '{{.State.Pid}}' $2`

sudo ln -s /proc/$OVS_PID/ns/net /var/run/netns/$OVS_PID
sudo ln -s /proc/$TCPR_PID/ns/net /var/run/netns/$TCPR_PID

PEER_A="veth_ovs"
PEER_B="veth_tcpr"
IP_A=10.1.1.1/32
IP_B=10.1.1.2/32
# Create the "peer" interfaces and hand them out
sudo ip link add $PEER_B type veth peer name $PEER_A

sudo ip link set $PEER_A netns $OVS_PID
sudo ip netns exec $OVS_PID ip addr add $IP_A dev $PEER_A
sudo ip netns exec $OVS_PID ip link set $PEER_A up
sudo ip netns exec $OVS_PID ip route add $IP_B dev $PEER_A

sudo ip link set $PEER_B netns $TCPR_PID
sudo ip netns exec $TCPR_PID ip addr add $IP_B dev $PEER_B
sudo ip netns exec $TCPR_PID ip link set $PEER_B up
sudo ip netns exec $TCPR_PID ip route add $IP_A dev $PEER_B
