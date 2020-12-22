FROM centos:7.6.1810

RUN rpmkeys --import file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7 && \
    yum install -y epel-release.noarch  && \
    rpmkeys  --import file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7 && \
    yum -y install nginx  && \
    # Clean cache
    yum -y clean all



# create an unprivileged user
ENV APP_ROOT=/opt/app \
    USER_NAME=default \
    USER_UID=10001
ENV LC_ALL=en_US.UTF-8
WORKDIR ${APP_ROOT}
ENV HOME=${APP_ROOT}

RUN mkdir -p ${APP_ROOT}/bin && \
    chmod -R ug+x ${APP_ROOT}/bin && sync && \
    useradd -l -u ${USER_UID} -r -g 0 -d ${APP_ROOT} -s /sbin/nologin -c "${USER_NAME} user" ${USER_NAME} && \
    chown -R ${USER_UID}:0 ${APP_ROOT} && \
    chmod -R g=u ${APP_ROOT}

# builded spa
COPY build ${APP_ROOT}/nginx

# nginx conf file
COPY docker/nginx.conf /etc/nginx/conf.d

CMD nginx && tail -f  /var/log/nginx/*
