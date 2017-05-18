FROM registry.rnd.unicredit.eu/base/alpine-jre8:1.8.0

COPY target/scala-2.11/app.jar /opt/app/

EXPOSE 9100 9000

CMD java -javaagent:/opt/prometheus/jmx_prometheus_javaagent.jar=9100:/opt/prometheus/jmx-exporter.yml -jar /opt/app/app.jar
