import kafka.serializer.StringDecoder
import play.api.libs.json.Json
//import play.api.libs.json._
import org.apache.spark.streaming._
import org.apache.spark.streaming.kafka.KafkaUtils
import org.apache.spark.SparkConf
import org.apache.spark.SparkContext

import org.elasticsearch.spark._
//import elasticsearch-spark_2.10-2.2.0-beta1.EsSpark

object SparkConsumer {
    def main(args: Array[String]) {
        val brokers = "elk1:9092"
        val topicsSet = Set("test1")
        val kafkaParams = Map[String, String]("metadata.broker.list" -> brokers)
        // Create context with 2 second batch interval
        val sparkConf = new SparkConf().setMaster("local[2]").setAppName("SparkConsumer")
        //sparkConf.set("es.index.auto.create", "true")
        val ssc = new StreamingContext(sparkConf, Seconds(5))
        //sparkConf.set("es.index.auto.create", "true")
        //val sc = new SparkContext(sparkConf)
        val timestamp = (System.currentTimeMillis / 1000).toString
        val messages = KafkaUtils.createDirectStream[String, String, StringDecoder, StringDecoder](ssc, kafkaParams, topicsSet)
        messages.print()
        println(messages.getClass.getName)
        //val esMessages = messages.map(t => t -> t)(collection.breakOut): Map[P, T]
        //sc.makeRDD(Seq(esMessages)).saveToES("spark/docs")
        messages.foreachRDD(rdd => { rdd.map(data => Map("kafka" -> data._2)).saveToEs("spark/docs")})
        
        ssc.start()
        ssc.awaitTermination()
    }
}