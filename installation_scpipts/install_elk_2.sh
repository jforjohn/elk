#ubuntu trusty 14.04
##source1: https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-4-on-ubuntu-14-04,
#source2: https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-repositories.html

 ##install java
 #it may requires to type the root password
 #add the Oracle Java PPA to apt
cd $HOME
sudo add-apt-repository -y ppa:webupd8team/java
 #update your apt package database
sudo apt-get update
 #Install the latest stable version of Oracle Java and accept the license agreement that pops up
sudo apt-get -y install oracle-java8-installer

 ##install Elasticsearch 1.7.1
 #import the Elasticsearch public GPG key into apt  
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
 #create the Elasticsearch source list 
echo "deb http://packages.elastic.co/elasticsearch/1.7/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-1.7.list
#sudo apt-get update && sudo apt-get install elasticsearch

<<comment1
 #or download the tar file and then unzip it
cd $HOME
wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.7.1.tar.gz
tar xzf elasticsearch-1.7.1.tar.gz
comment1

 ##install kibana 4.1.1
<<comment2
cd $HOME
wget https://download.elastic.co/kibana/kibana/kibana-4.1.1-linux-x64.tar.gz
tar xzf kibana-4.1.1-linux-x64.tar.gz
comment2
 #copy the Kibana files to a more appropriate location
 sudo mkdir -p /opt/kibana
 sudo cp -R ~/kibana-4*/* /opt/kibana/
  #we need to have Kibana 4 start up when the machine boots so we need to have it run as a service
sudo wget --output-document="/etc/init.d/kibana4" https://raw.githubusercontent.com/akabdog/scripts/master/kibana4_init
sudo chmod +x /etc/init.d/kibana4


 ##install Logstash 1.5.4
<<comment3
cd $HOME
wget https://download.elastic.co/logstash/logstash/logstash-1.5.4.tar.gz
tar xzf logstash-1.5.4.tar.gz
comment3

 #download and install the Public Signing Key
#wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
 #add the repository definition to your /etc/apt/sources.list file
echo "deb http://packages.elasticsearch.org/logstash/1.5/debian stable main" | sudo tee -a /etc/apt/sources.list
#sudo apt-get update
#sudo apt-get install logstash

 ##install logstash-forwarder  
echo 'deb http://packages.elasticsearch.org/logstashforwarder/debian stable main' | sudo tee /etc/apt/sources.list.d/logstashforwarder.list
#wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -

sudo apt-get update
sudo apt-get install elasticsearch logstash logstash-forwarder
