#!/usr/bin/python
import sys
import time
import subprocess
from datetime import datetime
from kafka import SimpleProducer, KafkaClient
#from mapProtocols import mapProtocol
#from mapPorts import mapPort
#from mapTCPflags import mapTCPflag



def runProcess(exe):    
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
      retcode = p.poll() #returns None while subprocess is running
      line = p.stdout.readline()
      yield line
      if(retcode is not None):
        break

def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

if __name__ == "__main__":
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
    #brokerList = ["elk1:9092", "elk2:9092"]
    brokerList = ["192.168.56.101:9092","192.168.56.102:9092"]
    kafka = KafkaClient(brokerList)
    producer = SimpleProducer(kafka, async=True, batch_send=True, batch_send_every_n=10, batch_send_every_t=5)

    #sflowToolProc = subprocess.Popen("sflowtool -l -p 6343".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    #out, err = sflowToolProc.communicate()
    count = 0
    print "Producer starts..."

    for line in runProcess('sh sflowtool-wrapper.sh -l'.split()):
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
            sampleRate = fields[19][:-1]
            dateTime = int(time.time()*1000000)
            protoName = 0#mapProtocol(protocol)
            srcService = 0#mapPort(srcPort)
            dstService = 0#mapPort(dstPort)
            tcpFlagType = 0#mapTCPflag(tcpFlag)
            message = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(srcMAC,dstMAC,etherType,srcVlan,dstVlan,srcIP,dstIP,protocol,protoName,srcPort,srcService,dstPort,dstService,tcpFlag,tcpFlagType,packetSize,sampleRate,dateTime,count)
            try:
                producer.send_messages("netdata", message)
            except:
                print "1s sleep"
                time.sleep(1)
                producer.send_messages("netdata", message)
            #producer.send_messages("netdata2", message)
            print message
    #s.close()
