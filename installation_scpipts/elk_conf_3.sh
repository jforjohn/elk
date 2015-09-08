#ubuntu trusty 14.04
##source1: https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-4-on-ubuntu-14-04
##source2: https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-configuration.html

ES_HOME=$HOME/elasticsearch-1.7.1
ES_CONFIG=/etc/elasticsearch/elasticsearch.yml #$ES_HOME/config/elasticsearch.yml
KBN_HOME=/opt/kibana
KBN_CONFIG=$KBN_HOME/config/kibana.yml
IP_ETH1=`ifconfig eth1 | grep 'inet addr'| awk '{print $2;}'|awk '{split($0,a,":");print a[2]}'`
PORT=5003
LOG_CONFIG=/etc/logstash/conf.d
 #to restrict outside access to your Elasticsearch instance (port 9200), so outsiders can't read your data or shutdown your Elasticsearch cluster through the HTTP API
 #also we give a name to our cluster and our node which is used to discover and auto-join other nodes
ex $ES_CONFIG <<EOEX1
 :%s/#network.host:\zs.*//
 :%s/#network.host:/network.host: localhost/g
 :%s/#cluster.name:\zs.*//
 :%s/#cluster.name:/cluster.name: elk-cluster/g
 :%s/#node.name:\zs.*//
 :%s/#node.name:/node.name: "elk-node2"/g
 :x
EOEX1

<<comment1
 ##configure Elasticsearch to automatically start during bootup (in a SysV init distribution)
sudo update-rc.d elasticsearch defaults 95 10
 #else diable it or remove it
#sudo update-rc.d elasticsearch disable #or "remove"
comment1

<<comment2
 #this setting makes it so Kibana will only be accessible to the localhost. This is fine because we will use an Nginx reverse proxy to allow external access.
ex KBN_CONFIG<<EOEX3
 :%s/host: "0.0.0.0"/host: "localhost"/g
 :x
EOEX3
 
 ##install and set nginx
 #Because we configured Kibana to listen on localhost, we must set up a reverse proxy to allow external access to it. We will use Nginx for this purpose
sudo apt-get install nginx apache2-utils
sudo htpasswd -bc kibanaadmin kibana > auth/htpasswd
sudo touch /etc/nginx/conf.d/kibana.conf 
sudo cat <<EOF > /etc/nginx/conf.d/kibana.conf
 server {
  listen 80;
  server_name $IP_ETH0;
  auth_basic "Restricted Access";
  auth_basic_user_file /etc/nginx/htpasswd.users;

  location / {
   proxy_pass http://localhost:5601;
   proxy_http_version 1.1;
   proxy_set_header Upgrade \$http_upgrade;
   proxy_set_header Connection 'upgrade';
   proxy_set_header Host \$host;
   proxy_cache_bypass \$http_upgrade;  
   }
  }
EOF
sudo service nginx restart
comment2

 #add your Logstash Server's private IP address to the subjectAltName (SAN) field of the SSL certificate that we are about to generate
ex /etc/ssl/openssl.cnf <<EOEX
 :%s/ v3_ca ]/ v3_ca ]\rsubjectAltName = IP: $IP_ETH1/g
 :x
EOEX

mkdir $HOME/certs
cd $HOME
sudo openssl req -config /etc/ssl/openssl.cnf -x509 -days 3650 -batch -nodes -newkey rsa:2048 -keyout certs/logfwd.key -out certs/logfwd.crt

 #set up our "lumberjack" input (the protocol that Logstash Forwarder uses)
sudo touch /etc/logstash/conf.d/01-lumberjack-input.conf
sudo cat <<EOF > $LOG_CONFIG/01-lumberjack-input.conf
input {
  lumberjack {
        port => $PORT
        type => "logs"
        ssl_certificate => "$HOME/certs/logfwd.crt"
        ssl_key => "$HOME/certs/logfwd.key"
  }
}
EOF

 #syslog filter configuration. It will try to use "grok" to parse incoming syslog logs to make it structured and query-able
sudo touch $LOG_CONFIG/10-syslog.conf
sudo cat <<EOF > /etc/logstash/conf.d/10-syslog.conf
filter {
  if [type] == "syslog" {
    grok {
      match => { "message" => "%{SYSLOGTIMESTAMP:syslog_timestamp} %{SYSLOGHOST:syslog_hostname} %{DATA:syslog_program}(?:\[%{POSINT:syslog_pid}\])?: %{GREEDYDATA:syslog_message}" }
      add_field => [ "received_at", "%{@timestamp}" ]
      add_field => [ "received_from", "%{host}" ]
    }
    syslog_pri { }
    date {
      match => [ "syslog_timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
    }
  }
}
EOF
 
 #configures Logstash to store the logs in Elasticsearch. With this configuration, Logstash will also accept logs that do not match the filter, but the data will not be structured (e.g. unfiltered Nginx or Apache logs would appear as flat messages instead of categorizing messages by HTTP response codes, source IP addresses, served files, etc.)
sudo touch $LOG_CONFIG/30-lumberjack-output.conf
sudo cat <<EOF > $LOG_CONFIG/30-lumberjack-output.conf
output {
  elasticsearch { host => localhost protocol => "http" port => "9200" }
  stdout { codec => rubydebug }
}
EOF
 #this configures Logstash Forwarder to connect to your Logstash Server on port 5000 (the port that we specified an input for earlier), and uses the SSL certificate that we created earlier. The paths section specifies which log files to send (here we specify syslog and auth.log), and the type section specifies that these logs are of type "syslog* (which is the type that our filter is looking for).
sudo touch /etc/logstash-forwarder.conf
sudo cat <<EOF > /etc/logstash-forwarder.conf
{
  "network": {
    "servers": [ "$IP_ETH1:$PORT" ],
    "ssl ca": "$HOME/certs/logfwd.crt",
    "timeout": 15
  },

  "files": [
  {
      "paths": [
        "/var/log/syslog",
        "/var/log/auth.log"
      ],
      "fields": { "type": "syslog" }
  }
  ]
}
EOF

<<comment4
 #try to lock the process address space into RAM, preventing any Elasticsearch memory from being swapped out
ex $ES_CONFIG <<EOEX
 :%s/#bootstrap.mlockall: true/bootstrap.mlockall: true/g
 :x
EOEX

cd $ES_HOME
sudo su
ulimit -l unlimited
./bin/elasticsearch -d
comment4
