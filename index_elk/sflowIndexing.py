#!/usr/bin/python
import sys
import time
import subprocess
from datetime import datetime
from elasticsearch import Elasticsearch
#from mapProtocols import mapProtocol
#from mapPorts import mapPort
#from mapTCPflags import mapTCPflag

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#try:
#    s.bind((host, port))
#except socket.error as msg:
#    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
#    sys.exit()

#print 'Socket bind complete'

#s.listen(10)
#conn, addr = s.accept()
#print 'Connected with ' + addr[0] + ':' + str(addr[1])        
sflowToolProc = subprocess.Popen("/bin/sh /root/sflowtool-wrapper.sh -l -p 6343".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
es = Elasticsearch(['elasticsearch'], port=9200)
count = 0
for line in sflowToolProc.stdout:
    fields = line.split(",")
    count += 1
    if fields[0] == "FLOW":
        #reporterIP = fields[1]
        srcMAC = fields[4]
        dstMAC = fields[5]
        etherType = fields[6]
        srcVlan = fields[7]
        dstVlan = fields[8]
        srcIP = fields[9]
        dstIP = fields[10]
        protocol = fields[11]
        #ipTOS = fields[12]
        #ipTTL = fields[13]
        srcPort = fields[14]
        dstPort = fields[15]
        tcpFlag = fields[16]
        packetSize = fields[17]
        #ipSize = fields[18]
        sampleRate = fields[19]
        dateTime = int(time.time()*1000000)
        protoName = 0#mapProtocol(protocol)
        srcService = 0#mapPort(srcPort)
        dstService = 0#mapPort(dstPort)
        tcpFlagType = 0#mapTCPflag(tcpFlag)
        message = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(srcMAC,dstMAC,etherType,srcVlan,dstVlan,srcIP,dstIP,protocol,protoName,srcPort,srcService,dstPort,dstService,tcpFlag,tcpFlagType,packetSize,sampleRate,dateTime,count)
        print message

        
        es.index(index=str(sys.argv[1]), doc_type="sflow", id=count, body={"srcMAC": srcMAC, "dstMAC": dstMAC, "etherType": etherType, "srcVlan": srcVlan, "dstVlan": dstVlan, "srcIP": srcIP, "dstIP": dstIP, "protocol": protocol, "srcPort": srcPort, "dstPort": dstPort, "tcpFlag": tcpFlag, "packetSize": packetSize, "sampleRate": sampleRate, "packetCount": count, "timestamp": datetime.now()})

#s.close()