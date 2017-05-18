package boilerplate.akka.http.metrics

import java.util.Calendar
import java.io._

import akka.actor.ActorSystem
import akka.event.Logging
import akka.http.scaladsl.Http
import akka.http.scaladsl.server.Directives._
import akka.http.scaladsl.server.RouteResult.route2HandlerFlow
import akka.http.scaladsl.marshallers.sprayjson.SprayJsonSupport
import akka.stream.ActorMaterializer

import com.codahale.metrics.JvmAttributeGaugeSet
import com.codahale.metrics.jvm.{ThreadStatesGaugeSet, MemoryUsageGaugeSet, GarbageCollectorMetricSet, FileDescriptorRatioGauge}
import com.typesafe.config.ConfigFactory

import spray.json.DefaultJsonProtocol._
import spray.json._

import scala.util.Random


object Main extends App with SprayJsonSupport {
  val config = ConfigFactory.load()

  val metricRegistry = new com.codahale.metrics.MetricRegistry()
  // --- Register Jvm metrics ---
  metricRegistry.register("jvm.attribute", new JvmAttributeGaugeSet())
  metricRegistry.register("jvm.gc", new GarbageCollectorMetricSet())
  metricRegistry.register("jvm.memory", new MemoryUsageGaugeSet())
  metricRegistry.register("jvm.threads", new ThreadStatesGaugeSet())


  val getCheck = metricRegistry.counter("boilerplate_akka_http_metrics_get_check")
  val getIndex = metricRegistry.counter("boilerplate_akka_http_metrics_get_index")

  val reporter = com.codahale.metrics.JmxReporter.forRegistry(metricRegistry).build()
  reporter.start()
  implicit val system = ActorSystem.create()
  implicit val executionContext = system.dispatcher
  implicit val materializer = ActorMaterializer()
  val logApp = Logging(system.eventStream, this.getClass.getCanonicalName)
  logApp.info(" --- START ---")

  lazy val route =
    post {
      path("api" / "echo") {
        decodeRequest {
          entity(as[String]) { content: String =>
            complete(content)
          }
        }
      }
    } ~
    get {
      path ("/") {
        getIndex.inc()
        complete("Hello, World!")
      } ~
      path("api" / "ping") {
        complete("PONG!")
      } ~
      path("api" / "random"/ IntNumber) { chars =>
          val rnd = Random.alphanumeric.take(chars).mkString
          complete(rnd.toString)
      } ~
      path("api" / "check") {
        getCheck.inc()
        logApp.debug("Request: /api/check")
        val today = Calendar.getInstance().getTime()
        complete(Map("status" -> "up","time"->today.toString).toJson)
      }
    }
  Http().bindAndHandle(route, interface = "0.0.0.0", port = config.getInt("application.port"))
}




