#!/usr/bin/python
from kafka import KafkaConsumer
import signal
import sys
import logging


def closeConsumer(signum, frame):
  logger.info('\nSignal handler called with signal: %s' %(signum))
  consumer.close()
  sys.exit(1)

if __name__ == '__main__':

  #logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
  # create logger
  logger = logging.getLogger('kafka 2 es')
  logger.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  logDest = logging.StreamHandler()

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # add formatter to ch
  logDest.setFormatter(formatter)

  # add ch to logger
  logger.addHandler(logDest)

  # To consume latest messages and auto-commit offsets
  logger.info('Consumer%i starts' %(1))
  consumer = KafkaConsumer('my-topic',
                           group_id='sflow-logstash',
                           bootstrap_servers=['192.168.0.2:9092','192.168.0.3:9092','192.168.0.4:9092'])


  signal.signal(signal.SIGINT, closeConsumer)
  for message in consumer:
      # message value and key are raw bytes -- decode if necessary!
      # e.g., for unicode: `message.value.decode('utf-8')`
      logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                            message.offset, message.key,
                                            message.value))
      


'''
# consume earliest available messages, dont commit offsets
KafkaConsumer(auto_offset_reset='earliest', enable_auto_commit=False)

# consume json messages
KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('ascii')))

# consume msgpack
KafkaConsumer(value_deserializer=msgpack.unpackb)

# StopIteration if no message after 1sec
KafkaConsumer(consumer_timeout_ms=1000)

# Subscribe to a regex topic pattern
consumer = KafkaConsumer()
consumer.subscribe(pattern='^awesome.*')

# Use multiple consumers in parallel w/ 0.9 kafka brokers
# typically you would run each on a different server / process / CPU
consumer1 = KafkaConsumer('my-topic',
                          group_id='my-group',
                          bootstrap_servers='my.server.com')
consumer2 = KafkaConsumer('my-topic',
                          group_id='my-group',
                          bootstrap_servers='my.server.com')

from contextlib import closing
from kafka import KafkaConsumer
import argparse
import json
import requests
import time
import re
import socket
import signal
import sys
import threading


def Parser():
  parser = argparse.ArgumentParser()

  parser.add_argument(
    '-v', '--verbose', action='store_true')
  parser.add_argument(
    '-r', '--lookup', help='Perform reverse DNS lookups on IP addresses.', action='store_true')
  parser.add_argument(
    '-tx', '--wbuf', help='Length of ES write buffer.', type=int, default=100)
  parser.add_argument(
    '-i', '--indexname', help='Elasticsearch index name to use.', type=str)
  parser.add_argument(
    '-id', '--indexdate', help='Append date to provided index.', action='store_true')
  parser.add_argument(
    '-k', '--timekey', help='Name of pmacct dictionary key to use for index.', default='timestamp_start', type=str)
  parser.add_argument(
    '-c', '--cstring', help='Kafka metadata broker endpoint.', default='127.0.0.1:9092')
  parser.add_argument(
    '-q', '--topic', help='Kafka consumer topic.', required=True, type=str)
  parser.add_argument(
    '--skip-old-messages', help='Consume messages starting from the current offset, effectively discarding earlier messages.', default=False, type=bool)
  parser.add_argument(
    '-t', '--timeout', help='Elasticsearch read timeout.', type=int, default=1)
  parser.add_argument(
    '-s', '--elasticserver', help='Hostname and port of (e.g. localhost:9200) for ElasticSearch instance.', default='http://localhost:9200')

  return parser.parse_args()


def Log(msg):
  if args.verbose:
    print '[%i] %s' % (int(time.time()), msg)


def GetTopic(queue_params):
  exchange = Exchange(args.exchangename, args.exchangetype, durable=args.exchangedurable)
  queue    = Queue(args.queue, exchange=exchange, routing_key=args.queue, durable=args.queuedurable, queue_arguments=queue_params) 

  return queue


class MessageHandler:
  def __init__(self):
    self.payload = []


  def Accept(self, body, message):
    try:
      self.payload.append(self.EmbedData(body, message))
    except Exception, e:
      Log('Discarding message - failed to append to payload: %s' % e)

    if len(self.payload) >= args.wbuf:
      route = message.topic
      self.PushMessage(route)


  def CreateESIndex(self, route):
    datestr  = time.strftime('%Y-%m-%d')

    if args.indexname:
      index    = args.indexname
      indexstr = '%s-%s' % (index, datestr)
    else:
      index    = '%s-%s' % ('pmacct', route)
      indexstr = '%s-%s' % (index, datestr)

    return indexstr


  def GetPacketTimestamp(self, body):
    try:
      datestr = 'T'.join(body[args.timekey].split())

    except KeyError:
      Log('Message does not contain %s field: %s' % (args.timekey, body))
      raise

    return datestr


  def TimestampESFormat(self, timestamp):
    tz = re.search('([-+]\d+$)', timestamp)

    # Shave off extra data sent by pmacct and work out an appropriate tz.
    if tz:
      # TZ came with payload.
      timestamp = timestamp[0:23] + tz.groups()[0]
    else:
      # This timestamp may not include timezone; lets pretend it is this one.
      timestamp = '%s%s' % (timestamp[0:23], time.strftime('%z'))

    return timestamp


  def EmbedData(self, body, message):
    tags = []
    if 'tags' in body: tags += body['tags']
    # tags.append(message.delivery_info['routing_key'])
    body['tags'] = tags
    timestamp = self.GetPacketTimestamp(body)
    body['@timestamp'] = self.TimestampESFormat(timestamp)

    if args.lookup:
      if 'ip_dst' in body:
        try:
          destination = socket.gethostbyaddr(body['ip_dst'])[0]
          body['ip_dst_ptr'] = destination
        except: pass
      if 'ip_src' in body:
        try:
          source = socket.gethostbyaddr(body['ip_src'])[0]
          body['ip_src_ptr'] = source
        except: pass

    return body


  def Encapsulate(self, route):
    index = self.CreateESIndex(route)

    header = {
      'index': {
        '_type' : 'pmacct',
        '_index': index,
      }
    }

    Log('Compiling Elasticsearch payload with %i records' % len(self.payload))
    header = json.dumps(header)
    body   = ''
    data   = ''

    for record in self.payload:
      data += '%s\n%s\n' % (header, json.dumps(record))

    return data
  

  def PushMessage(self, route):
    data = self.Encapsulate(route)

    try:
      r = requests.post('%s/_bulk?' % args.elasticserver, data=data, timeout=args.timeout)
      self.payload = []
      Log('Bulk API request to Elasticsearch returned with code %i' % r.status_code)
    except Exception, e:
      Log('Failed to send to Elasticsearch: %s' % e)


class MessageConsumer:
  def __init__(self, connection, callback):
    self.callback   = callback
    self.connection = connection


  def close(self, *args, **kwargs):
    Log('Shutdown')
    self.connection.close()
    exit(0)


  def run(self):
    for message in self.connection:
      body = json.loads(message.value)
      self.callback(body, message)


def SetupConsumer():
  if args.skip_old_messages:
    auto_offset_reset = 'largest'
  else:
    auto_offset_reset = 'smallest'

  output = KafkaConsumer(
    args.topic,
    auto_offset_reset=auto_offset_reset,
    group_id='pmacct_%s' % args.topic,
    bootstrap_servers=args.cstring,
  )

  return output


if __name__ == "__main__":
  global args
  args = Parser()

  connection = SetupConsumer()
  handler    = MessageHandler()
  consumer   = MessageConsumer(connection, handler.Accept)

  signal.signal(signal.SIGINT, connection.close)

  closing(consumer.run())
'''