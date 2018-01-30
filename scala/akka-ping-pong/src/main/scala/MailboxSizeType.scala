/**
 * Copyright (C) 2009-2014 Typesafe Inc. <http://www.typesafe.com>
 *
 *   https://gist.github.com/patriknw/5946678
 *
 */
package boilerplate.akka.pingpong

import java.util.concurrent.atomic.AtomicInteger
import com.typesafe.config.Config
import akka.actor.{ ActorRef, ActorSystem }
import akka.dispatch.{ Envelope, MailboxType, MessageQueue, UnboundedMailbox, ProducesMessageQueue }
import akka.event.Logging

import java.lang.management.ManagementFactory
import javax.management.{ ObjectName, MBeanServer }
/**
 * Logs the mailbox size when exceeding the configured limit. It logs at most once per second
 * when the messages are enqueued or dequeued.
 *
 * Configuration:
 * <pre>
 * akka.actor.default-mailbox {
 *   mailbox-type = akka.contrib.mailbox.LoggingMailboxType
 *   size-limit = 20
 * }
 * </pre>
 */
class MailboxSizeType(settings: ActorSystem.Settings, config: Config) extends MailboxType with ProducesMessageQueue[UnboundedMailbox.MessageQueue] {
  override def create(owner: Option[ActorRef], system: Option[ActorSystem]) = (owner, system) match {
    case (Some(o), Some(s)) =>
      val sizeLimit = 100 //config.getInt("size-limit")
      val mailbox = new MailboxSize(o, s, sizeLimit)
      // register mbean
      val path = o.path.toString
      mailbox
    case _ => throw new IllegalArgumentException("no mailbox owner or system given")
  }
}

class MailboxSize(owner: ActorRef, system: ActorSystem, sizeLimit: Int)
  extends UnboundedMailbox.MessageQueue {

  private lazy val log = Logging(system, classOf[MailboxSize])
  private val path = owner.path.toString

  val mailboxSizeBean = new OrderTracker
  val mbs: MBeanServer = ManagementFactory.getPlatformMBeanServer()
  val mBeanName: ObjectName = new ObjectName(s"metrics.akka.mailbox.size:type=MailboxSize,path=${owner.path.toStringWithoutAddress}")
  mbs.registerMBean(mailboxSizeBean, mBeanName)

  println(s"Create mailbox for path: ${path} name ${owner.path.toStringWithoutAddress}")
  private val queueSize = new AtomicInteger

  override def dequeue(): Envelope = {
    val x = super.dequeue()
    if (x ne null) {
      queueSize.decrementAndGet()
    }
    x
  }

  override def enqueue(receiver: ActorRef, handle: Envelope): Unit = {
    super.enqueue(receiver, handle)
    val size = queueSize.incrementAndGet()
    mailboxSizeBean.setSize(size)
  }

  override def cleanUp(owner: ActorRef, deadLetters: MessageQueue): Unit = {
    super.cleanUp(owner, deadLetters)
  }
}
