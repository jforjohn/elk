#!/usr/bin/python
from kafka import KafkaConsumer
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from elasticsearch import Elasticsearch, helpers
#from translateIP import mapIP
import logging
import signal
import sys
import yaml
from yaml import load
from yaml import CLoader as Loader
import time, datetime

class MessageHandler:
  def __init__(self):
    self.data = dict()
    self.send_data = list()

  def Accept(self, body, message, es):
    try:
      #self.payload.append(self.EmbedData(body))
      self.data = self.EmbedData(body)
    except Exception, e:
      loggerConsumer.error('Discarding message - failed to append to payload: %s' % e)

    self.Encapsulate()
    print len(self.send_data)
    if len(self.send_data) >= 1500:
      #topic = message.topic
      self.PushMessage(es)

  def EmbedData(self, body):
    sflowSample = dict()
    '''
    timestamp = 'T'.join(
                str(datetime.datetime.now())
               .split())[0:23] + 'Z'
    '''
    timestamp = int(time.time() * 1000)
    
    print timestamp
    fields = body.split(',')
    if fields[0] == "FLOW":
      sflow_ReporterIP = fields[1]
      sflow_inputPort = fields[2]
      sflow_outputPort = fields[3]
      sflow_srcMAC = fields[4]
      sflow_dstMAC = fields[5]
      sflow_EtherType = fields[6]
      sflow_srcVlan = fields[7]
      sflow_dstVlan = fields[8]
      sflow_srcIP = fields[9]
      sflow_dstIP = fields[10]
      sflow_IP_Protocol = fields[11]
      sflow_IPTOS = fields[12]
      sflow_IPTTL = fields[13]
      sflow_srcPort = fields[14]
      sflow_dstPort = fields[15]
      sflow_tcpFlags = fields[16]
      sflow_PacketSize = fields[17]
      sflow_IPSize = fields[18]
      sflow_SampleRate = fields[19]
      try:
        sflow_counter = fields[20]
      except:
        sflow_counter = -1
      #dateTime = int(time.time()*1000000)
      
      #[sflow_NEWsrcIP,sflow_NEWdstIP] = map(mapIP, [sflow_srcIP,sflow_dstIP])
      #srcIPnew = mapIP(srcIP)
      #dstIPnew = mapIP(dstIP)
      [sflow_NEWsrcIP, sflow_NEWdstIP] = map(self.mapIP, [sflow_srcIP,sflow_dstIP])

      [sflow_inputPort,sflow_outputPort,sflow_srcVlan,sflow_dstVlan,sflow_IP_Protocol,sflow_IPTTL,sflow_srcPort,sflow_dstPort,sflow_PacketSize,sflow_IPSize,sflow_SampleRate,sflow_SampleRate] = map(int, [sflow_inputPort,sflow_outputPort,sflow_srcVlan,sflow_dstVlan,sflow_IP_Protocol,sflow_IPTTL,sflow_srcPort,sflow_dstPort,sflow_PacketSize,sflow_IPSize,sflow_SampleRate,sflow_SampleRate])

      sflowSample = {
      '@message':body,
      '@timestamp':timestamp,
      '@version':1,
      'type':'sflow',
      'SampleType':'FLOW',
      'sflow_ReporterIP':sflow_ReporterIP,
      'sflow_inputPort':sflow_inputPort,
      'sflow_outputPort':sflow_outputPort,
      'sflow_srcMAC':sflow_srcMAC,
      'sflow_dstMAC':sflow_dstMAC,
      'sflow_EtherType':sflow_EtherType,
      'sflow_srcVlan':sflow_srcVlan,
      'sflow_dstVlan':sflow_dstVlan,
      'sflow_srcIP':sflow_srcIP,
      'sflow_dstIP':sflow_dstIP,
      'sflow_IP_Protocol':sflow_IP_Protocol,
      'sflow_IPTOS':sflow_IPTOS,
      'sflow_IPTTL':sflow_IPTTL,
      'sflow_srcPort':sflow_srcPort,
      'sflow_dstPort':sflow_dstPort,
      'sflow_tcpFlags':sflow_tcpFlags,
      'sflow_PacketSize':sflow_PacketSize,
      'sflow_IPSize':sflow_IPSize,
      'sflow_SampleRate':sflow_SampleRate,
      'sflow_NEWsrcIP':sflow_NEWsrcIP,
      'sflow_NEWdstIP':sflow_NEWdstIP
      }
    else:
      sflowSample = {'type':body}

    return sflowSample

  def mapIP(self,param):
    try:
      return test[param]
    except:
      return param

  def Encapsulate(self):
    datestr  = time.strftime('%Y.%m.%d')
    indexstr = '%s-%s' % ('sflow', datestr)
    
    self.send_data.append({
      '_index' : indexstr,
      '_type': 'sflow',
      '_source': self.data
      
    })
    
    loggerIndex.info('Compiling Elasticsearch payload with  records') #% len(self.payload))
    #header = json.dumps(header)
    #body   = ''
    #data   = ''

    #for record in self.payload:
    #  data += '%s\n%s\n' % (header, json.dumps(record))

    #return send_data

  def PushMessage(self, es):
    try:
      #r = requests.post('%s/_bulk?' % args.elasticserver, data=data, timeout=args.timeout)
      #helpers.parallel_bulk(es, data, chunk_size=5)
      for success, info in helpers.parallel_bulk(es, self.send_data, chunk_size=1500):
        #print '\n', info, success
        print info, success
        if not success:
          print('A document failed:', info)
      self.data = {}
      self.send_data = []
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
                            max_partition_fetch_bytes=20000000,
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
  global test
  # create logger

  stream = open("jsonIPmap.yaml", 'r')
  test = yaml.load(stream, Loader=Loader)
  
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
