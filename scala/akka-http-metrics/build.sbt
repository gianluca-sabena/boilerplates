
name := """akka-http-metrics"""

version := "1.0-SNAPSHOT"

scalaVersion := "2.11.8"

//enablePlugins(JavaAppPackaging)

lazy val akkaVersion = "2.4.11"

resolvers += "Typesafe Releases" at "https://repo.typesafe.com/typesafe/releases/"

libraryDependencies ++= Seq(
  "com.typesafe.akka" %% "akka-http-core" % akkaVersion,
  "com.typesafe.akka" %% "akka-stream" % akkaVersion,
  "com.typesafe.akka" %% "akka-http-spray-json-experimental" % akkaVersion,
  "com.typesafe.akka"     %% "akka-slf4j"     % akkaVersion,
  "io.dropwizard.metrics" % "metrics-core"     % "3.1.2",
  "io.dropwizard.metrics" % "metrics-jvm"     % "3.1.2",
  "com.typesafe.scala-logging" %% "scala-logging" % "3.5.0",
  "ch.qos.logback"        % "logback-classic" % "1.1.3",
  "com.typesafe.akka" %% "akka-http-testkit" % "2.4.11",
  "org.scalatest" %% "scalatest" % "3.0.0" % "test"
)

test in assembly := {}

assemblyJarName in assembly := "app.jar"

mainClass in assembly := Some("boilerplate.akka.http.metrics.Main")


