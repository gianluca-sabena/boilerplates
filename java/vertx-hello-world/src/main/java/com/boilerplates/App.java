/*
 * Based on <https://github.com/reactiverse/vertx-maven-plugin/tree/master/samples/custom-main-example/src/main/java/org/vertx/demo>
 */
package com.boilerplates;

import io.vertx.core.DeploymentOptions;
import io.vertx.core.Vertx;
import io.vertx.core.json.JsonObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

  private static final Logger logger = LoggerFactory.getLogger(App.class);

  public static void main(String[] args) {
    logger.info("--- Start ---");
    DeploymentOptions dOpt =
        new DeploymentOptions().setConfig(new JsonObject().put("message", "Ola"));
    Vertx vertx = Vertx.vertx();
    // vertx.deployVerticle(SimpleVerticle.class.getName(),dOpt);
    // vertx.deployVerticle(FutureVerticle.class, dOpt);
    vertx.deployVerticle(WebVerticle.class, dOpt);
  }
}

// public class App {
//     public String getGreeting() {
//         return "Hello world.";
//     }

//     public static void main(String[] args) {
//         System.out.println(new App().getGreeting());
//     }
// }
