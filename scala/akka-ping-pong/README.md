# Akka ping pong

Exchange messages between two actors

## Metrics

- Export to jmx
- Use codahale metrics

## Run

Run with sbt
- `sbt run`

Create a docker
- build uber jar `sbt assembly`
- build docker image with `docker build -t akka-ping-pong .`
- run docker with `docker run -t -i akka-ping-pong`

## Jvisulavm

Jvisualvm can shows Jmx metrics:

- Open plugin and add a repository https://visualvm.github.io/uc/8u131/updates.xml.gz
- Search and install VisualVM-MBeans plugin
- Get random Jmx/Jvisual port from DCOS web UI
- Open JvisualVm and click on "Add jmx connection" and select "do not require ssl connection"

## Logging

SLF4J is the logging interface
logback is a Logging backend compatible with SLF4J

- use scala logging (logging library wrapping SLF4J) from outside of an actor class/library
- use akka-slf4j inside actors
