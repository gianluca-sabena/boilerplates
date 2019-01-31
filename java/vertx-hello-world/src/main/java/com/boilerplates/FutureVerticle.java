package com.boilerplates;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Future;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FutureVerticle extends AbstractVerticle {

  private final Logger logger = LoggerFactory.getLogger(FutureVerticle.class);

  // Start with a future https://vertx.io/docs/guide-for-java-devs/#_anatomy_of_a_verticle
  @Override
  public void start(Future<Void> startFuture) {
    logger.info("--- Start ---");
    vertx
        .createHttpServer()
        .requestHandler(
            req -> {
              req.response().putHeader("Content-Type", "plain/text").end("Yo!");
              logger.info(
                  "Handled a request on path {} from {}", req.path(), req.remoteAddress().host());
            })
        .listen(
            8081,
            ar -> {
              if (ar.succeeded()) {
                startFuture.complete();
              } else {
                startFuture.fail(ar.cause());
              }
            });
  }
}
