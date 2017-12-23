package boilerplate.akka.pingpong

import akka.actor.{ Actor, ActorLogging, ActorRef, Props }

object Pong {

  def props() = Props(new Pong())

}

class Pong() extends Actor with ActorLogging {
  import Data._
  def receive = {
    case PingMessage =>
      sender ! PongMessage
    case StopMessage =>
      log.info("pong stopped")
      context.stop(self)
    case m: Any => log.error(s"Received unmatched message ${m.toString}")
  }
}