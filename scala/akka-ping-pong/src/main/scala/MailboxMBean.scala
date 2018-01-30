package boilerplate.akka.pingpong

import java.util.concurrent.atomic.AtomicInteger

trait OrderTrackerMBean {
  def getSize: Int
  def setSize(orderId: Int)
}

class OrderTracker extends OrderTrackerMBean {
  private val size = new AtomicInteger
  override def getSize: Int = size.get()
  override def setSize(_size: Int) = {
    size.set(_size)
  }

}