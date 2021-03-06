FROM centos:centos7

#
# --- Set env variables ---
#
ENV LC_ALL="en_US.UTF-8"
ENV LANG="en_US.UTF-8"
ENV TZ="Europe/Rome"

#
# --- Add user and and allow random uid ---
#
ENV APP_ROOT="/opt/app"
ENV USER_NAME="app"
ENV USER_UID="10001"
ENV PATH="${APP_ROOT}/bin:$PATH"
#COPY docker/bin/ ${APP_ROOT}/bin/
# allow to run random user id (openshift compatibility)
RUN useradd -l -u ${USER_UID} -r -g 0 -d ${APP_ROOT} -s /sbin/nologin -c "${USER_NAME} user" ${USER_NAME} && \
    mkdir -p ${APP_ROOT}/bin && \
    chmod -R u+x ${APP_ROOT}/bin && \
    chgrp -R 0 ${APP_ROOT} && \
    chmod -R g=u ${APP_ROOT} /etc/passwd

#
# --- Build tesseract ---
# - see https://github.com/EisenVault/install-tesseract-redhat-centos/blob/master/install-tesseract.sh

ENV LEPTONICA_VERSION="1.74.4"
ENV TESSERACT_VERSION="4.0.0"
RUN curl -sS http://www.leptonica.org/source/leptonica-${LEPTONICA_VERSION}.tar.gz  | tar xvz -C ./opt 
RUN curl -sSL https://github.com/tesseract-ocr/tesseract/archive/4.0.0.tar.gz  | tar xvz -C ./opt 
RUN rpmkeys --import file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7 && \
    yum install -y  gcc gcc-c++ file make pkg-config autoconf automake libtool  libstdc++ autoconf-archive libjpeg-devel libpng-devel libtiff-devel zlib-devel && \
    cd /opt/leptonica-${LEPTONICA_VERSION} && \
    ./configure && \
    make && \
    make install && \
    cd /opt && \
    rm -rf /opt/leptonica-${LEPTONICA_VERSION} && \
    cd /opt/tesseract-${TESSERACT_VERSION} && \
    ./autogen.sh && \
    PKG_CONFIG_PATH=/usr/local/lib/pkgconfig LIBLEPT_HEADERSDIR=/usr/local/include ./configure --with-extra-includes=/usr/local/include --with-extra-libraries=/usr/local/lib && \
    make && \
    make install && \
    rm -rf /opt/tesseract-${TESSERACT_VERSION} && \
    yum remove -y gcc gcc-c++ make pkg-config autoconf automake libtool  autoconf-archive libjpeg-devel libpng-devel libtiff-devel zlib-devel  && \
    yum clean all

#
# --- Pyenv and pipenv ---
#
ENV PY_VERSION="3.7.2"
ENV PYENV_ROOT="${APP_ROOT}/pyenv"
# add shim to path, this avoid running pyenv init -
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:$PATH"
# install env in project with
ENV PIPENV_VENV_IN_PROJECT=true
RUN rpmkeys --import file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7 && \
    yum install -y  gcc gcc-c++ make git patch openssl-devel zlib-devel readline-devel sqlite-devel bzip2-devel libffi-devel which && \
    git clone --branch v1.2.13 git://github.com/yyuu/pyenv.git ${PYENV_ROOT} && \
    pyenv install "$PY_VERSION" && \
    pyenv global ${PY_VERSION} && \
    pip install --upgrade pip && \
    pip install pipenv && \
    pyenv rehash && \
    yum remove -y gcc gcc-c++ make patch openssl-devel zlib-devel readline-devel sqlite-devel bzip2-devel  && \
    yum clean all 


#
# --- Copy app source ---
#
# COPY Pipfile ${APP_ROOT}/Pipfile
# RUN cd ${APP_ROOT} && \
#     pipenv  install --skip-lock 
# COPY src ${APP_ROOT}/src

#
# --- Final ---
#
# Containers should NOT run as root as a good practice
# USER ${USER_UID}
WORKDIR ${APP_ROOT}

CMD pipenv run python -u src/main.py
