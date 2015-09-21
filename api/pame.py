sflow_fields=[u'sflow.srcIP', u'sflow.dstIP',u'sflow.dstPort'] 
sflow_values=[u'10.1.1.1', u'10.2.2.2',u'80']
sendto_clusters=[u'elk-vm1', u'elk-vm2',u'elk-vm1']

DIR='/home/nectar/elk/compose_elk/logstash/config'
filename='sflow_output.conf'
try:
    conf_file = open(DIR+'/'+filename,'w')
except:
    print 'File cannot be opened:', filename
conf_file.write('output {\n     if [type] == "sflow" {\n        stdout { codec => rubydebug }\n')
changes = sorted(zip(sendto_clusters,sflow_fields,sflow_values))
init = changes[0][0] 
newIF = True
#TODO make a name for elasticsearch host
#TODO run forward sflow from logstash-forwarfer to logstash
#TODO run docker-compose for elk with the appropriate link names

for cluster,field,value in changes:
    if cluster != init:
        conf_file.write('{\n            elasticsearch { protocol => "http"  cluster => "%s" host => elasticsearch}\n    }\n' %(init))
        newIF = True
        init = cluster
    if newIF == True:
        conf_file.write('        if [%s] == "%s" ' %(field,value))
    else:
        conf_file.write('and [%s] == "%s"' %(field,value))
    newIF = False
conf_file.write('{\n            elasticsearch { protocol => "http"  cluster => "%s" host => elasticsearch}\n    }\n}' %(init))
conf_file.close()
