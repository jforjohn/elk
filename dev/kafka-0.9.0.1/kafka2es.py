#!/usr/bin/python
from kafka import KafkaConsumer
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from elasticsearch import Elasticsearch, helpers
from translateIP import mapIP
import logging
import signal
import sys
import json
import time, datetime

class MessageHandler:
  def __init__(self):
    self.data = dict()

  def Accept(self, body, message, es):
    try:
      #self.payload.append(self.EmbedData(body))
      self.data = self.EmbedData(body)
    except Exception, e:
      loggerConsumer.error('Discarding message - failed to append to payload: %s' % e)

    #if len(self.payload) >= 10:
    topic = message.topic
    self.PushMessage(topic, es)

  def EmbedData(self, body):
    sflowSample = dict()
    
    #sflowSample['@timestamp']
    timestamp = 'T'.join(
                str(datetime.datetime.now())
               .split())[0:23] + 'Z'

    fields = body.split(',')
    if fields[0] == "FLOW":
      #reporterIP = fields[1]
      #inPort = fields[2]
      #outPort = fields[3]
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

      
      [srcIPnew, dstIPnew] = map(mapIP, [srcIP,dstIP])
      #srcIPnew = mapIP(srcIP)
      #dstIPnew = mapIP(dstIP)

      sflowSample = {
      #'reporterIP':reporterIP,
      #'inPort':inPort,
      #'outPort':outPort
      '@timestamp':timestamp,
      'srcMAC':srcMAC,
      'dstMAC':dstMAC,
      'etherType':etherType,
      'srcVlan':srcVlan,
      'dstVlan':dstVlan,
      'srcIP':srcIP,
      'dstIP':dstIP,
      'protocol':protocol,
      #'ipTOS':ipTOS,
      #'ipTTL':ipTTL,
      'srcPort':srcPort,
      'dstPort':dstPort,
      'tcpFlag':tcpFlag,
      'packetSize':packetSize,
      #'ipSize':ipSize,
      'sampleRate':sampleRate,
      'srcIPnew':srcIPnew,
      'dstIPnew':dstIPnew
      }
    else:
      sflowSample = body

    return sflowSample

  def Encapsulate(self):
    datestr  = time.strftime('%Y-%m-%d')
    indexstr = '%s-%s' % ('sflow1', datestr)
    
    send_data = [{
      '_index' : indexstr,
      '_type': 'sflow',
      '_source': self.data
      
    }]
    
    loggerIndex.info('Compiling Elasticsearch payload with  records') #% len(self.payload))
    #header = json.dumps(header)
    #body   = ''
    #data   = ''

    #for record in self.payload:
    #  data += '%s\n%s\n' % (header, json.dumps(record))

    return send_data

  def PushMessage(self, topic, es):
    send_data = self.Encapsulate()
    try:
      #r = requests.post('%s/_bulk?' % args.elasticserver, data=data, timeout=args.timeout)
      #helpers.parallel_bulk(es, data, chunk_size=5)
      for success, info in helpers.parallel_bulk(es, send_data, chunk_size=200):
        print '\n', info, success
        if not success:
          print('A document failed:', info)
      self.data = {}
      loggerIndex.info('Bulk API request to Elasticsearch returned with code ' )
    except Exception, e:
      loggerIndex.error('Failed to send to Elasticsearch: %s' % e)


class StreamConsumer():
  def __init__(self, connection, es, callback):
    self.callback   = callback
    self.connection = connection
    self.es = es

  #def close(self, *args, **kwargs):
    #self.connection.close()
    #exit(0)
  def closeConsumer(signum, frame, self):
    loggerConsumer.info('Signal handler called with signal: %s' %(signum))
    self.connection.close()
    sys.exit(0)

  def runConsumer(self):
    try:
      for message in self.connection:
        body = message.value #json.loads(message.value)
        self.callback(body, message, self.es)
    except Exception, e:
      loggerConsumer.error("During messages parsing exception: %s" %e)


def SetupConsumer():
  # To consume latest messages and auto-commit offsets
  loggerConsumer.info('Consumer%i starts' %(1)) 
  try:
    myConsumer = KafkaConsumer('connect-test',
                            group_id='sflow-myConsumerz',
                            bootstrap_servers=['192.168.0.2:9092','192.168.0.3:9092','192.168.0.4:9092'],
                            #max_partition_fetch_bytes=20000000,
                            partition_assignment_strategy=[RoundRobinPartitionAssignor])
  except Exception, e:
    loggerConsumer.error("During consumer instantiation: %s" %e)
  return myConsumer

def SetupES():
  loggerIndex.info('Connecting to Elasticsearch cluster')
  try:
    es = Elasticsearch(["192.168.0.1", "192.168.0.4", "192.168.0.5"],
          sniff_on_start=True,
          sniff_on_connection_fail=True,
          sniffer_timeout=120)
  except Exception, e:
    loggerConsumer.error("During Elasticsearch cluster instantiation: %s" %e)
  return es

if __name__ == '__main__':
  global loggerConsumer
  global loggerIndex
  # create logger
  loggerConsumer = logging.getLogger('kafka consumer')
  loggerConsumer.setLevel(logging.DEBUG)

  loggerIndex = logging.getLogger('es indexing')
  loggerConsumer.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  logDest = logging.StreamHandler()

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # add formatter to ch
  logDest.setFormatter(formatter)

  # add ch to logger
  loggerConsumer.addHandler(logDest)
  loggerIndex.addHandler(logDest)
  
  kafkaConnection = SetupConsumer()
  esConnection = SetupES()
  handler = MessageHandler()

  consumer = StreamConsumer(kafkaConnection, esConnection, handler.Accept)

  signal.signal(signal.SIGINT, consumer.closeConsumer)

  consumer.runConsumer()
