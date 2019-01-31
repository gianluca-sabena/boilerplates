/*
 * Based on <https://vertx.io/blog/some-rest-with-vert-x/>
 */
package com.boilerplates;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Future;
import io.vertx.core.http.HttpServerResponse;
import io.vertx.ext.web.Route;
import io.vertx.ext.web.Router;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WebVerticle extends AbstractVerticle {

  private final Logger logger = LoggerFactory.getLogger(WebVerticle.class);

  // Start with a future https://vertx.io/docs/guide-for-java-devs/#_anatomy_of_a_verticle
  @Override
  public void start(Future<Void> startFuture) {
    logger.info("--- Start ---");
    // Create a router object.
    Router router = Router.router(vertx);

    // Bind "/" to our hello message - so we are still compatible.
    router
        .route("/")
        .handler(
            routingContext -> {
              HttpServerResponse response = routingContext.response();
              response
                  .putHeader("content-type", "text/html")
                  .end("<h1>Hello from my first Vert.x 3 application</h1>");
            });

    Route routeChain = router.route("/example/chain/");
    routeChain.handler(
        routingContext -> {
          HttpServerResponse response = routingContext.response();
          // enable chunked responses because we will be adding data as
          // we execute over other handlers. This is only required once and
          // only if several handlers do output.
          response.setChunked(true);

          response.write("route1\n");

          // Call the next matching route after a 3 second delay
          // Note, all this happens without any thread blocking.
          routingContext.vertx().setTimer(3000, tid -> routingContext.next());
        });

    routeChain.handler(
        routingContext -> {
          HttpServerResponse response = routingContext.response();
          response.write("route2\n");

          // Call the next matching route after a 3 second delay
          // Note, all this happens without any thread blocking.
          routingContext.vertx().setTimer(3000, tid -> routingContext.next());
        });

    routeChain.handler(
        routingContext -> {
          HttpServerResponse response = routingContext.response();
          response.write("route3");

          // Now end the response
          routingContext.response().end();
        });

    // Create the HTTP server and pass the "accept" method to the request handler.
    vertx
        .createHttpServer()
        .requestHandler(router)
        .listen(
            // Retrieve the port from the configuration,
            // default to 8080.
            config().getInteger("http.port", 8082),
            result -> {
              if (result.succeeded()) {
                startFuture.complete();
              } else {
                startFuture.fail(result.cause());
              }
            });
  }
}
