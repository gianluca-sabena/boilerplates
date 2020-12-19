FROM centos:7.6.1810 

RUN yum -y install epel-release \
    && yum -y install python36 gcc python36-devel python36-pip nginx uwsgi uwsgi-plugin-python36 \
    && ln -s /usr/bin/python3.6 /usr/bin/python3 \
    && ln -s /usr/bin/pip3.6 /usr/bin/pip3 \
    && pip3 install --upgrade pip 
ENV LC_ALL=en_US.UTF-8
RUN pip3 install Flask  \
    && localedef -i en_US -f UTF-8 en_US.UTF-8

COPY src /opt/app/src
COPY config/flask.ini /opt/app/config/flask.ini
COPY config/nginx.conf /etc/nginx/conf.d

# create an unprivileged user
ENV APP_ROOT=/opt/app \
    USER_NAME=default \
    USER_UID=10001

WORKDIR ${APP_ROOT}
ENV HOME=${APP_ROOT}

RUN mkdir -p ${APP_ROOT}/bin && \
    chmod -R ug+x ${APP_ROOT}/bin && sync && \
    useradd -l -u ${USER_UID} -r -g 0 -d ${APP_ROOT} -s /sbin/nologin -c "${USER_NAME} user" ${USER_NAME} && \
    chown -R ${USER_UID}:0 ${APP_ROOT} && \
    chmod -R g=u ${APP_ROOT}

CMD nginx && uwsgi /opt/app/config/flask.ini && tail -f  /var/log/nginx/* /var/log/uwsgi.log

#docker run -t -i -p 8080:8080 -p 9090:9090 -p 9191:9191 flask
# run flask cd /opt/app && FLASK_APP=src/hello-world flask run
#RUN python setup.py install
#RUN python setup.py develop


#uwsgi --plugin /usr/lib64/uwsgi/python36_plugin.so --http-socket 127.0.0.1:9000 --wsgi-file hello-world.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191 