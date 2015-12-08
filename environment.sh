#!/bin/bash

USER=/home/nectar
export PATH=$PATH:$USER/apache-maven-3.3.9/bin
export HADOOP_HOME=$USER/hadoop-2.7.1
#export JAVA_HOME=/usr
#export SCALA_HOME=/usr
export PATH=$HADOOP_HOME/bin:$PATH
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_INSTALL/lib/native
export HADOOP_OPTS="-Djava.library.path=$HADOOP_INSTALL/lib"
#export SPARK_CLASSPATH=/home/nectar/spark-1.5.2-bin-hadoop2.6/elasticsearch-hadoop-2.2.0-beta1/dist
export CLASSPATH=/home/nectar/spark-1.5.2-bin-hadoop2.6/elasticsearch-hadoop-2.2.0-beta1/dist
