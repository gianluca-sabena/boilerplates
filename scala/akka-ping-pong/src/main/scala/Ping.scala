package boilerplate.akka.pingpong

import akka.actor.{ Actor, ActorLogging, ActorRef, Props }
import com.typesafe.config.ConfigFactory

object Ping {
  def props(pong: ActorRef) = Props(new Ping(pong))
}

class Ping(pong: ActorRef) extends Actor with ActorLogging {
  val config = ConfigFactory.load()
  val app = config.getString("application.app")
  val messagesTotal = config.getInt("application.messages")
  import Data._
  var messages = 1;
  def receive = {
    case StartMessage =>
      pong ! PingMessage
    case PongMessage =>
      if (messages % 1000 == 0) log.info("Received 1000 messages")
      if (messages == messagesTotal) {
        self ! StopMessage
      }
      else {
        messages += 1
        pong ! PingMessage
      }
    case StopMessage =>
      log.info("ping stopped")
      pong ! StopMessage
      context.stop(self)
      context.system.terminate()
    case m: Any =>
      log.warning(s"Received unmatched message ${m.toString}")
  }
}