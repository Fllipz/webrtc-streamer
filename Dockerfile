FROM ubuntu:20.10

# install Husarnet client
RUN apt update -y && \
    apt install -y curl && \
    apt install -y gnupg2 && \
    apt install -y systemd && \
    curl https://install.husarnet.com/install.sh | bash

RUN update-alternatives --set ip6tables /usr/sbin/ip6tables-nft

# install webserver service
RUN apt install -y nginx

# some optional modules
RUN apt install -y vim
RUN apt install -y iputils-ping

# Find your JOINCODE at https://app.husarnet.com
ENV JOINCODE=""
ENV HOSTNAME=my-container-1

# HTTP PORT
EXPOSE 80

RUN apt update -y
RUN apt-get update -y

RUN apt-get install -y ffmpeg

# Install janus dependencies
RUN apt-get install -y \
    build-essential \
    libmicrohttpd-dev \
    libjansson-dev \
    libnice-dev \
    libssl-dev \
    libsofia-sip-ua-dev \
    libglib2.0-dev \
    libopus-dev \
    libogg-dev \
    libini-config-dev \
    libcollection-dev \
    pkg-config \
    gengetopt \
    libtool \
    autotools-dev \
    automake \
    libconfig-dev

RUN apt-get install -y \
	git \
	make \
	sudo 

# Install libsrtp
RUN cd ~ \
    && git clone https://github.com/cisco/libsrtp.git \
    && cd libsrtp \
    && git checkout v2.2.0 \
    && ./configure --prefix=/usr --enable-openssl \
    && make shared_library \
    && sudo make install

# Install janus
RUN cd ~ \
&& git clone https://github.com/meetecho/janus-gateway.git \
&& cd janus-gateway \
&& sh autogen.sh \
&& ./configure --disable-websockets --disable-data-channels --disable-rabbitmq --disable-docs --prefix=/opt/janus \
&& make \
&& sudo make install \
&& sudo make configs

# Configure janus
COPY conf/*.jcfg  /opt/janus/etc/janus/

EXPOSE 80 7088 8088 8188 8089
EXPOSE 10000-10200/udp
EXPOSE 8000-8010/udp

# copy project files into the image
COPY init-container.sh /opt
COPY *.sh /opt/
COPY src /var/www/html/

# initialize a container
RUN cp -r /opt/janus/share/janus/demos/. /var/www/html
COPY src /var/www/html/
RUN cp -r /opt/janus/share/janus/demos/ /var/www/html
CMD /opt/init-container.sh

