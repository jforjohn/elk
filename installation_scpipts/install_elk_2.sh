#ubuntu trusty 14.04
##source1: https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-4-on-ubuntu-14-04,
#source2: https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-repositories.html

 ##install java
 #it may requires to type the root password
 #add the Oracle Java PPA to apt
sudo add-apt-repository -y ppa:webupd8team/java
 #update your apt package database
sudo apt-get update
 #Install the latest stable version of Oracle Java and accept the license agreement that pops up
sudo apt-get -y install oracle-java8-installer

 ##install Elasticsearch
 #import the Elasticsearch public GPG key into apt  

 <<comment1
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
 #create the Elasticsearch source list 
echo "deb http://packages.elastic.co/elasticsearch/1.7/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-1.7.list
sudo apt-get update && sudo apt-get install elasticsearch
comment1

 ##configure Elasticsearch to automatically start during bootup (in a SysV init distribution)
sudo update-rc.d elasticsearch defaults 95 10
#else diable it or remove it
#sudo update-rc.d elasticsearch disable #or "remove"
 
 #or download the tar file and then unzip it
cd $HOME
wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.7.1.tar.gz
tar xzf elasticsearch-1.7.1.tar.gz



