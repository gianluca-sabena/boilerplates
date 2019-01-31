package com.boilerplates;

import java.net.URI;
import java.net.URISyntaxException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import io.undertow.Undertow;
import io.undertow.server.handlers.proxy.LoadBalancingProxyClient;
import io.undertow.server.handlers.proxy.ProxyHandler;


class Server {
  Logger logger = LoggerFactory.getLogger(Server.class);
  
  public void buildAndStartServer() throws URISyntaxException {
    logger.info("Server starting...");
    LoadBalancingProxyClient loadBalancer;
      loadBalancer = new LoadBalancingProxyClient().addHost(new URI("http://minio:9000"))
          .setConnectionsPerThread(20);
    ProxyHandler proxyHandler = ProxyHandler.builder().setProxyClient(loadBalancer).setMaxRequestTime(30000).build();

    // HttpHandler finalHandler = new HttpHandler() {
    //   @Override
    //   public void handleRequest(final HttpServerExchange exchange) throws Exception {
    //     logger.info("Final handler");
    //     exchange.getResponseHeaders().put(Headers.CONTENT_TYPE, "text/plain");
    //     exchange.getResponseSender().send("Hello World");
    //   }
    // };

    Undertow server = Undertow.builder().addHttpListener(9090, "0.0.0.0").setIoThreads(4)
        .setHandler(proxyHandler).build();
    server.start();

  }
}