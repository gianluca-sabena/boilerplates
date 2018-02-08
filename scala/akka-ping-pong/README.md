# Akka ping pong

Exchange messages between two actors

## Metrics

- Export to jmx
- Use codahale metrics with akka actor system extension

TODO: Separate and improve jmx and codahale mailbox objects

## Run

Run with sbt
- `sbt run`

Create a docker and:

- build uber jar `sbt assembly`
- build docker image with `docker build -t akka-ping-pong .`
- run docker with `docker run -t -i akka-ping-pong`

## Out of memory

Produce java out of memory exception with an unbounded mailbox

Run with `java -XX:+CrashOnOutOfMemoryError -Xmx256m -Dapplication.pause-before-start=45000 -Dapplication.ping-factor=1000  -jar target/scala-2.11/app.jar`

Use Java mission control to see GC pressure from a mailbox

## Logging

SLF4J is the logging interface
logback is a Logging backend compatible with SLF4J

- use scala logging (logging library wrapping SLF4J) from outside of an actor class/library
- use akka-slf4j inside actors

## Java mission control

Java profile with Java Mission Control

... todo ... debug memory leaks..

## Jvisulavm

Jvisualvm can shows Jmx metrics:

- Open plugin and add a repository https://visualvm.github.io/uc/8u131/updates.xml.gz
- Search and install VisualVM-MBeans plugin
- Get random Jmx/Jvisual port from DCOS web UI
- Open JvisualVm and click on "Add jmx connection" and select "do not require ssl connection"


