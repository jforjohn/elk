import sbtassembly.AssemblyPlugin._

name := "SparkConsumer"

version := "1.0"

scalaVersion := "2.10.6"

libraryDependencies ++= Seq("org.apache.spark" %% "spark-core" % "1.5.2",
                            "org.apache.spark" %% "spark-streaming" % "1.5.2",
                            "org.apache.spark" %% "spark-streaming-kafka" % "1.5.2",
                            "org.apache.kafka" % "kafka_2.10" % "0.8.2.0",
                            "com.typesafe.play" %% "play-json" % "2.3.4")

resolvers += "Typesafe Repo" at "http://repo.typesafe.com/typesafe/releases/"   

unmanagedJars in Compile := (baseDirectory.value ** "*.jar").classpath

assemblyMergeStrategy in assembly := {
    case PathList("javax", "servlet", xs @ _*) => MergeStrategy.last
    case PathList("javax", "activation", xs @ _*) => MergeStrategy.last
    case PathList("org", "apache", xs @ _*) => MergeStrategy.last
    case PathList("com", "google", xs @ _*) => MergeStrategy.last
    case PathList("com", "esotericsoftware", xs @ _*) => MergeStrategy.last
    case PathList("com", "codahale", xs @ _*) => MergeStrategy.last
    case PathList("com", "yammer", xs @ _*) => MergeStrategy.last
    case "about.html" => MergeStrategy.rename
    case "META-INF/ECLIPSEF.RSA" => MergeStrategy.last
    case "META-INF/mailcap" => MergeStrategy.last
    case "META-INF/mimetypes.default" => MergeStrategy.last
    case "plugin.properties" => MergeStrategy.last
    case "log4j.properties" => MergeStrategy.last
    case x =>
        val oldStrategy = (assemblyMergeStrategy in assembly).value
        oldStrategy(x)
}                            
