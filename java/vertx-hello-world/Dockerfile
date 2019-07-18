FROM centos:7

RUN yum clean all \
    && yum -y install java-11-openjdk\
    && yum clean all

COPY build/libs/vertx-hello-world-all.jar  /opt

CMD java -jar /opt/vertx-hello-world-all.jar