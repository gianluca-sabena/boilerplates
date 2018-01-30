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
  var latencyTimer = metricRegistry.timer("latency")
  def props(pong: ActorRef) = Props(new Ping(pong))
}

class Ping(pong: ActorRef) extends Actor with ActorLogging {
  val config = ConfigFactory.load()
  val app = config.getString("application.app")
  val messagesTotal = config.getInt("application.messages")
  val pingFactor = config.getInt("application.ping-factor")
  val iterationsTotal = config.getInt("application.iterations")
  var iteration = 0
  var startTs = 0L
  import Data._
  import Ping._
  var messages = 0
  var messagesSent = 0
  def receive = {
    case StartMessage =>
      startTs = System.nanoTime()
      iteration += 1
      messages = 0
      messagesSent = 1
      log.info(s"Start iteration $iteration of $iterationsTotal")
      pong ! PingMessage(System.nanoTime())
    case PongMessage(latency: Long) =>
      messages += 1
      if (messages <= messagesTotal) {
        messagesSent += pingFactor
        latencyTimer.update(System.nanoTime() - latency, TimeUnit.NANOSECONDS)
        if (pingFactor == 1) pong ! PingMessage(System.nanoTime())
        else {
          // Simulate a MAILBOX overflow!!!
          for (i <- 1 to pingFactor) {
            pong ! PingMessage(System.nanoTime())
          }
        }
      }
      else if (messages == messagesSent) self ! NextIteration

    case NextIteration =>
      log.info("ping stopped")
      val elapsed = System.nanoTime() - startTs
      slf4jReporter.report()
      log.info(s" Processed ${messagesTotal} messages in ${elapsed / 1000000} milliseconds")
      Thread.sleep(1000)
      if (iteration < iterationsTotal) self ! StartMessage
      else self ! StopMessage

    case StopMessage =>
      context.stop(self)
      context.system.terminate()

    case m: Any =>
      log.warning(s"Received unmatched message ${m.toString}")
  }
}