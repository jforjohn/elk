#!/bin/bash
 #install pip
sudo apt-get install python-pip

 #install virtualenv, which  is a tool to create isolated Python environments
#wget https://pypi.python.org/packages/source/v/virtualenv/virtualenv-13.1.2.tar.gz#md5=b989598f068d64b32dead530eb25589a
sudo apt-get install python-virtualenv
#mkdir flask-api
#cd flask-api
virtualenv flask 
flask/bin/pip install flask 

##clocker + calico
#sudo modprobe xt_set 
#sudo modprobe ipip
