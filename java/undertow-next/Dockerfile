FROM openjdk:11.0.2-jdk-oraclelinux7
#FROM openjdk:8u181-jdk
RUN mkdir /logs
ADD build/libs/undertow-next.jar /
CMD java -jar undertow-next.jar