package boilerplate.akka.pingpong

import java.util.concurrent.TimeUnit

import akka.actor.{ Actor, ActorLogging, ActorRef, Props }
import com.codahale.metrics.MetricRegistry
import com.typesafe.config.ConfigFactory

object Ping {
  val metricRegistry = new MetricRegistry()

  import com.codahale.metrics.Slf4jReporter
  import org.slf4j.LoggerFactory
  import java.util.concurrent.TimeUnit

  val slf4jReporter = Slf4jReporter.forRegistry(metricRegistry)
    .outputTo(LoggerFactory.getLogger("boilerplate.grpc.metrics"))
    .convertRatesTo(TimeUnit.SECONDS)
    .convertDurationsTo(TimeUnit.MICROSECONDS)
    .build
  val latencyTimer = metricRegistry.timer("latency")
  def props(pong: ActorRef) = Props(new Ping(pong))
}

class Ping(pong: ActorRef) extends Actor with ActorLogging {
  val config = ConfigFactory.load()
  val app = config.getString("application.app")
  val messagesTotal = config.getInt("application.messages")
  val pingFactor = config.getInt("application.ping-factor")
  import Data._
  import Ping._
  var messages = 1
  def receive = {
    case StartMessage =>
      pong ! PingMessage(System.nanoTime())
    case PongMessage(latency: Long) =>
      if (messages % 1000 == 0) log.debug("Received 1000 messages")
      if (messages == messagesTotal) {
        self ! StopMessage
      }
      else {
        messages += 1
        latencyTimer.update(System.nanoTime() - latency, TimeUnit.NANOSECONDS)
        if (pingFactor == 1) pong ! PingMessage(System.nanoTime())
        else {
          // Simulate a MAILBOX overflow!!!
          for (i <- 1 to pingFactor) {
            pong ! PingMessage(System.nanoTime())
          }
        }

      }
    case StopMessage =>
      log.info("ping stopped")
      pong ! StopMessage
      slf4jReporter.report()
      context.stop(self)
      context.system.terminate()

    case m: Any =>
      log.warning(s"Received unmatched message ${m.toString}")
  }
}