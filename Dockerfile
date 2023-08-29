FROM gilleslamiral/imapsync as img1
# FROM python:3.9.10-alpine3.14 as img2
USER root
COPY Dockerfile imapsyn[c] prerequisites_imapsyn[c] /

RUN set -xe && \
  apt-get update \
  && apt-get install -y \
  libauthen-ntlm-perl \
  libcgi-pm-perl \
  libcrypt-openssl-rsa-perl \
  libdata-uniqid-perl \
  libencode-imaputf7-perl \
  libfile-copy-recursive-perl \
  libfile-tail-perl \
  libio-compress-perl \
  libio-socket-ssl-perl \
  libio-socket-inet6-perl \
  libio-tee-perl \
  libhtml-parser-perl \
  libjson-webtoken-perl \
  libmail-imapclient-perl \
  libparse-recdescent-perl \
  libmodule-scandeps-perl \
  libpar-packer-perl \
  libreadonly-perl \
  libregexp-common-perl \
  libsys-meminfo-perl \
  libterm-readkey-perl \
  libtest-mockobject-perl \
  libtest-pod-perl \
  libunicode-string-perl \
  liburi-perl  \
  libwww-perl \
  procps \
  wget \
  make \
  cpanminus \
  lsof \
  ncat \
  openssl \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/* \
  && cpanm IO::Socket::SSL

# I added the IO::Socket::SSL update to avoid the annoying, confusing and useless warning
# DEBUG: .../IO/Socket/SSL.pm:1177: global error: Undefined SSL object

RUN set -xe \
  && cd /usr/bin/ \
  && pwd \
  && wget -N --no-check-certificate https://imapsync.lamiral.info/imapsync \
        https://imapsync.lamiral.info/prerequisites_imapsync \
        https://raw.githubusercontent.com/google/gmail-oauth2-tools/master/python/oauth2.py \
  && chmod +x imapsync oauth2.py

USER nobody:nogroup

ENV HOME /var/tmp/
ENV LANG C.UTF-8

WORKDIR /var/tmp/

STOPSIGNAL SIGINT

USER root
WORKDIR /srv
RUN apt update
RUN apt install -y software-properties-common
# RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y python3-launchpadlib
RUN apt-get install -y python3-pip python3-venv
# RUN pip install --upgrade pip3
RUN pip install flask --break-system-packages
COPY . /srv
ENV FLASK_APP=app
CMD ["flask","--app", "api", "run", "--host", "0.0.0.0"]