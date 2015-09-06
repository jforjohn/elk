#ubuntu trusty 14.04
##source1: https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-4-on-ubuntu-14-04
##source2: https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-configuration.html

ES_HOME=$HOME/elasticsearch-1.7.1
ES_CONFIG=$ES_HOME/config/elasticsearch.yml #/etc/elasticsearch/elasticsearch.yml
KBN_HOME=$HOME/kibana-4.1.1-linux-x64
KBN_CONFIG=$KIBANA_HOME/config/kibana.yml
IP_ETH0=`ifconfig eth0 | grep 'inet addr'| awk '{print $2;}'|awk '{split($0,a,":");print a[2]}'`

 #to restrict outside access to your Elasticsearch instance (port 9200), so outsiders can't read your data or shutdown your Elasticsearch cluster through the HTTP API
 #also we give a name to our cluster and our node which is used to discover and auto-join other nodes
ex $ES_CONFIG <<EOEX1
 :%s/#network.host:\zs.*//
 :%s/#network.host:/network.host: localhost/g
 :%s/#cluster.name:\zs.*//
 :%s/#cluster.name:/cluster.name: elk-cluster/g
 :%s/#node.name:\zs.*//
 :%s/#node.name:/node.name: \${prompt.text}
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
touch /etc/nginx/conf.d/kibana.conf 
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

<<comment3
 #copy the Kibana files to a more appropriate location
sudo mkdir -p /opt/kibana
sudo cp -R ~/kibana-4*/* /opt/kibana/
 #we need to have Kibana 4 start up when the machine boots so we need to have it run as a service
sudo wget --output-document="/etc/init.d/kibana4" https://raw.githubusercontent.com/akabdog/scripts/master/kibana4_init
sudo chmod +x /etc/init.d/kibana4

#sudo service kibana4 start
comment3

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


