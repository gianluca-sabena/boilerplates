package boilerplate.akka.pingpong

object Data {
  case class PingMessage(latency: Long)
  case class PongMessage(latency: Long)
  case object StartMessage
  case object StopMessage
  case object NextIteration
}