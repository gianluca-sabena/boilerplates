/*
 * Based on <https://github.com/reactiverse/vertx-maven-plugin/tree/master/samples/custom-main-example/src/main/java/org/vertx/demo>
 */
package com.boilerplates;

import io.vertx.core.AbstractVerticle;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SimpleVerticle extends AbstractVerticle {

  private final Logger logger = LoggerFactory.getLogger(SimpleVerticle.class);

  // Start without a future https://vertx.io/docs/guide-for-java-devs/#_anatomy_of_a_verticle
  @Override
  public void start() {
    logger.info("--- Start ---");
    vertx
        .createHttpServer()
        .requestHandler(
            req -> req.response().end(config().getString("message") + " World, it works !"))
        .listen(8080);
  }
}
