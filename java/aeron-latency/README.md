# Aeron latency 

Based on aeron examples <https://github.com/real-logic/aeron/tree/master/aeron-samples/src/main/java/io/aeron/samples>

## Run

Local run requires an embedded media driver.
PongThread starts the media driver, PingThread connects to it by settings the same media driver folder.

### With maven

Use exec plugin with two exec id

- Start ping `mvn compile exec:java@ping` (see pom.xml for custom args)
- Start pong `mvn compile exec:java@pong` (see pom.xml for custom args)

### With a jar

Compile uber jar with `mvn package `

Start Pong first

```bash
java -cp target/aeron-latency-1.0-SNAPSHOT.jar \
-Daeron.sample.embeddedMediaDriver=true  \
boilerplates.aeron.latency.Pong
```

Start Ping

```bash
java -cp target/aeron-latency-1.0-SNAPSHOT.jar \
boilerplates.aeron.latency.Ping
```

### Start on different host

