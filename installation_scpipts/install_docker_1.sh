#ubuntu trusty 14.04
##source1: https://docs.docker.com/installation/ubuntulinux/

##install docker
 ##install wget
sudo apt-get update
sudo apt-get install wget
wget -qO- https://get.docker.com/ | sudo sh
 #run docker without sudo in the beginning
sudo usermod -aG docker $USER
 #log out and log in again !
