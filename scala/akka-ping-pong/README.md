# Akka ping pong

Exchange messages between two actors

## Metrics

- Export to jmx
- Use codahale metrics

## Kamon.io

This project uses [kamon.io](http://kamon.io) to track akka metrics
See/edit [build.sbt](./build.sbt) and [application.conf](./src/main/resources/application.conf) to enable/disable log and jmx reporter

Kamon is a **great** project but it poor documented and it use aspectj to rewrite bytecode (this may add some overhead and is not suitable for production environment)

Overview:

- add kamon dependencies
- add settings to application.conf
- start kamon from main (before anything else)
- use sbt-plugin to load aspectj local
- use a custom assembly strategy to create a uber.jar compatible with aspectjweaver [Gist](https://gist.github.com/colestanfield/fac042d3108b0c06e952) [Issue](https://github.com/kamon-io/Kamon/issues/59)
- run java in docker with javaagent:/pat-to-aspectj.jar

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
