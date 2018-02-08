/**
 * Extend actor system for codahale metric registry
 *
 *   - https://doc.akka.io/docs/akka/2.5/extending-akka.html
 *
 */

package boilerplate.akka.pingpong

import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicLong

import akka.actor.{ Actor, ActorSystem, ExtendedActorSystem, Extension, ExtensionId, ExtensionIdProvider }
import com.codahale.metrics.{ MetricRegistry, SharedMetricRegistries, Slf4jReporter }
import org.slf4j.LoggerFactory

object MetricExtension
  extends ExtensionId[MetricExtensionImpl]
  with ExtensionIdProvider {
  //The lookup method is required by ExtensionIdProvider,
  // so we return ourselves here, this allows us
  // to configure our extension to be loaded when
  // the ActorSystem starts up
  override def lookup = MetricExtension

  //This method will be called by Akka
  // to instantiate our Extension
  override def createExtension(system: ExtendedActorSystem) = new MetricExtensionImpl

  /**
   * Java API: retrieve the Count extension for the given system.
   */
  override def get(system: ActorSystem): MetricExtensionImpl = super.get(system)
}

class MetricExtensionImpl extends Extension {
  //Since this Extension is a shared instance
  // per ActorSystem we need to be threadsafe
  private val counter = new AtomicLong(0)
  private val metricRegistry = new MetricRegistry()

  private val slf4jReporter = Slf4jReporter.forRegistry(metricRegistry)
    .outputTo(LoggerFactory.getLogger("boilerplate.grpc.metrics"))
    .convertRatesTo(TimeUnit.SECONDS)
    .convertDurationsTo(TimeUnit.MICROSECONDS)
    .build

  //This is the operation this Extension provides
  def increment() = counter.incrementAndGet()

  def getCounter(name: String) = metricRegistry.counter(name)
  def getTimer(name: String) = metricRegistry.timer(name)

  def slf4jReport() = slf4jReporter.report()
}

trait Metric { self: Actor ⇒
  def increment() = MetricExtension(context.system).increment()
  def getMetricCounter(name: String) = MetricExtension(context.system).getCounter(name)
  def getMetricTimer(name: String) = MetricExtension(context.system).getTimer(name)
  def slf4jReport() = MetricExtension(context.system).slf4jReport()
}