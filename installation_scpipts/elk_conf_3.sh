#ubuntu trusty 14.04
##source1: https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-4-on-ubuntu-14-04
##source2: https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-configuration.html

ES_HOME=$HOME/elasticsearch-1.7.1
ES_CONFIG=$ES_HOME/config/elasticsearch.yml #/etc/elasticsearch/elasticsearch.yml

 #to restrict outside access to your Elasticsearch instance (port 9200), so outsiders can't read your data or shutdown your Elasticsearch cluster through the HTTP API
 #also we give a name to our cluster and our node which is used to discover and auto-join other nodes
ex $ES_CONFIG <<EOEX1
 :%s/#network.host:\zs.*//
 :%s/#network.host:/network.host: localhost/g
 :%s/#cluster.name:\zs.*//
 :%s/#cluster.name:/cluster.name: elk-cluster/g
 :%s/#node.name:\zs.*//
 :%s/#node.name:/node.name: "elk-node"/g
 :x
EOEX1

<<comment1
 ##configure Elasticsearch to automatically start during bootup (in a SysV init distribution)
sudo update-rc.d elasticsearch defaults 95 10
 #else diable it or remove it
#sudo update-rc.d elasticsearch disable #or "remove"
comment1

<<comment2
 #try to lock the process address space into RAM, preventing any Elasticsearch memory from being swapped out
ex $ES_CONFIG <<EOEX
 :%s/#bootstrap.mlockall: true/bootstrap.mlockall: true/g
 :x
EOEX

cd $ES_HOME
sudo su
ulimit -l unlimited
./bin/elasticsearch -d
comment2


