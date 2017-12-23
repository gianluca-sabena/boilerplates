FROM openjdk:8u151-jre-alpine

COPY target/scala-2.11/app.jar /opt/app/

# Required for kamon
# RUN curl -sSo /opt/aspectjweaver.jar  http://central.maven.org/maven2/org/aspectj/aspectjweaver/1.8.12/aspectjweaver-1.8.12.jar

CMD java -jar /opt/app/app.jar


