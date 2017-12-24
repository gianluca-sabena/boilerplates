package boilerplate.akka.pingpong

import java.util.concurrent.TimeUnit

import akka.actor.{ ActorSystem, Props }
import akka.event.Logging
import akka.routing.RoundRobinPool
import boilerplate.akka.pingpong.Data.StartMessage
import com.codahale.metrics.jvm.{ GarbageCollectorMetricSet, MemoryUsageGaugeSet, ThreadStatesGaugeSet }
import com.codahale.metrics.{ JmxReporter, JvmAttributeGaugeSet, MetricRegistry, Slf4jReporter }
import com.typesafe.config.ConfigFactory
import com.typesafe.scalalogging.Logger

import scala.concurrent.Await
import scala.concurrent.duration._

object Main extends App {

  val config = ConfigFactory.load()
  val app = config.getString("application.app")
  val project = config.getString("application.project")
  val logger = Logger(s"$project.$app")
  val sleepBeforeStart = config.getInt("application.pause-before-start")

  import Data._

  // Init codahale metrics
  val metricRegistry = new MetricRegistry()
  metricRegistry.register("jvm.attribute", new JvmAttributeGaugeSet())
  metricRegistry.register("jvm.gc", new GarbageCollectorMetricSet())
  metricRegistry.register("jvm.memory", new MemoryUsageGaugeSet())
  metricRegistry.register("jvm.threads", new ThreadStatesGaugeSet())

  // Create an actor system
  val system = ActorSystem("actor-system")
  logger.info(s"Sleep ${sleepBeforeStart} ms ...")
  Thread.sleep(sleepBeforeStart)
  logger.info("\n----------\n--- START ---\n----------")

  // Create actors
  val pongActor = system.actorOf(Pong.props(), "pong-actor")
  val pingActor = system.actorOf(Ping.props(pongActor), "ping-actor")

  pingActor ! StartMessage

  // Catch a Ctrl+C = sig term OR
  // In a shell run `# kill -TERM $pid`
  // mesos termination https://github.com/mesosphere/marathon/issues/4323
  scala.sys.addShutdownHook {
    logger.info("\n----------\n--- SHUTDOWN ---\n----------")
    println("Terminating...")
    system.terminate()
    Await.result(system.whenTerminated, Duration.create(30, SECONDS))
    println("Terminated... Bye")
  }
}

