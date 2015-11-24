# elk

## Real time network traffic monitoring and PaaS provisioning

The project here is part of my thesis. The topic is to monitor sampled network traffic (sflow) and then provide it as Platform as a Service to end users. 

- 1st stage: I have chosen to use ELK stack (Elasticsearch, Logstash, Kibana) and ES-Hadoop. There are many ways to feed the data into Elasticsearch database apart from Logstash. I have implemented various ways and architectures to do this using Kafka, Spark and Elasticsearch API and I am goind to compare them in order to see what fits better to my use case.

- 2nd stage: Concerning the PaaS provisioning, I am using Docker and the goal is to use either Clocker, Kubernetes or Tumtum in order to provide containers with Elasticsearch and Kibana with data filtered for every seperate end user. Thus, the end users will be able to see their traffic they are interested in and then any analytics experiments with these data.

- Future plans: There are more stuff you can do with all these. As a future work on this projeject, I plan to automate the whole system even more using an application manager or orchestrator like Apache Brooklyn which will provide or take back resources depending on the traffic volume and the preprocessing. The results of the benc Last but not least, I want to develop and use some tools for offline analytics and anomaly detection using Spark and [Prelert](http://info.prelert.com/anomaly-detection-in-elasticsearch). 



