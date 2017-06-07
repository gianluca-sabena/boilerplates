import io.undertow.Undertow;
import io.undertow.server.HttpHandler;
import io.undertow.server.HttpServerExchange;
import io.undertow.util.Headers;

import com.codahale.metrics.*;
import com.codahale.metrics.jvm.*;

public class HelloWorldServer {
    

    public static void main(final String[] args) {
        // metrics
        final MetricRegistry metrics = new MetricRegistry();
        // start JMX reporter
        JmxReporter.forRegistry(metrics).build().start();
        // jvm metrics
        metrics.register("jvm.attribute", new JvmAttributeGaugeSet());
        metrics.register("jvm.gc", new GarbageCollectorMetricSet());
        metrics.register("jvm.memory", new MemoryUsageGaugeSet());
        metrics.register("jvm.threads", new ThreadStatesGaugeSet());
        // create a counter metrics
        final Counter requests = metrics.counter(MetricRegistry.name("boilerplates","undertow","hello-world","counter", "home"));
        // main undertow
        Undertow server = Undertow.builder().addHttpListener(8080, "localhost").setHandler(new HttpHandler() {
            @Override
            public void handleRequest(final HttpServerExchange exchange) throws Exception {
                requests.inc();
                exchange.getResponseHeaders().put(Headers.CONTENT_TYPE, "text/plain");
                exchange.getResponseSender().send("Hello World");
            }
        }).build();
        server.start();

    }
}
