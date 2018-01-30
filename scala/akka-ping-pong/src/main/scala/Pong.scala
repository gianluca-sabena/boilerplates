package boilerplate.akka.pingpong

import akka.actor.{ Actor, ActorLogging, ActorRef, Props }
import com.typesafe.config.ConfigFactory

object Pong {

  def props() = Props(new Pong())

}

class Pong() extends Actor with ActorLogging {
  import Data._
  def receive = {
    case PingMessage(latency: Long) =>
      sender ! PongMessage(latency)
    case StopMessage =>
      log.info("pong stopped")
      context.stop(self)
    case m: Any => log.error(s"Received unmatched message ${m.toString}")
  }
}