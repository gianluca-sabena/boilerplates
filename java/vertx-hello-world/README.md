# Vert.x example

Eclipse Vert.x is a tool-kit for building reactive applications on the JVM

Architecture and intro <https://vertx.io/docs/guide-for-java-devs/#_introduction>

Features:

- event loop and thread from worker pool <https://vertx.io/docs/guide-for-java-devs/#_core_vert_x_concepts>
- actor like concurrency <https://vertx.io/docs/vertx-core/java/#_verticles>
- internal event bus <https://vertx.io/docs/vertx-core/java/#event_bus>
- multiple protocol: udp, tcp, http, grpc, ...

Example is based on

- Run verticle from main <https://github.com/reactiverse/vertx-maven-plugin/tree/master/samples/custom-main-example/src/main/java/org/vertx/demo>
- A simple http server async with future and junit5 test <https://github.com/vert-x3/vertx-examples/blob/master/junit5-examples/src/main/java/hello/SampleVerticle.java>

## Build

Run `./gradlew run`

Test `./gradlew test`