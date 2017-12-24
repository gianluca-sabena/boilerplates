import com.typesafe.sbt.SbtScalariform.ScalariformKeys
import scalariform.formatter.preferences._

lazy val akkaVersion = "2.5.8"

ScalariformKeys.preferences := ScalariformKeys.preferences.value
  .setPreference(DanglingCloseParenthesis, Force)
  .setPreference(SpacesWithinPatternBinders, false)
  .setPreference(CompactControlReadability, true)


lazy val commonSettings = Seq(
  version := "1.0-SNAPSHOT",
  scalaVersion := "2.11.12",
  resolvers += Resolver.jcenterRepo,
  scalacOptions in ThisBuild ++= Seq(
    "-feature",
    "-deprecation",
    "-target:jvm-1.8"),
  libraryDependencies ++= Seq(
    "com.typesafe.akka" %% "akka-actor" % akkaVersion,
    "com.typesafe.akka" %% "akka-testkit" % akkaVersion,
    "com.typesafe.akka" %% "akka-slf4j" % akkaVersion,
    "io.dropwizard.metrics" % "metrics-core" % "3.2.3",
    "io.dropwizard.metrics" % "metrics-jvm" % "3.2.3",
    "com.typesafe.scala-logging" %% "scala-logging" % "3.7.2",
    "ch.qos.logback" % "logback-classic" % "1.2.1",
    "org.scalatest" %% "scalatest" % "2.2.6" % "test"
  ),
  assemblyJarName in assembly := "app.jar",
  assemblyMergeStrategy in assembly := {
    case PathList("META-INF", xs @ _ *) => MergeStrategy.discard
    case x =>
      val oldStrategy = (assemblyMergeStrategy in assembly).value
      oldStrategy(x)
  }
)

lazy val root = (project in file("."))
  .settings(commonSettings: _*)
  .settings(
  name := "akka-ping-pong",
  fork in run := true
  // cancelable in Global := true, // enable ctrl+c to kill task
  // connectInput in run := true
)

