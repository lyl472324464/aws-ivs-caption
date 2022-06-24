FROM ubuntu:20.04
#FROM buildpack-deps:stretch
ENV DEBIAN_FRONTEND=noninteractive
# Versions of Nginx and nginx-rtmp-module to use
ENV NGINX_VERSION nginx-1.18.0
ENV NGINX_RTMP_MODULE_VERSION 1.2.1

# Install dependencies Stunnel4
RUN apt-get update && \
    apt-get install -y ca-certificates openssl libssl-dev stunnel4 gettext && \
    rm -rf /var/lib/apt/lists/*

#Install wget
RUN apt-get update && \
    apt-get install -y wget

#Install libpcre3-dev zlib1g-dev libssl-dev
RUN apt-get install -y libpcre3-dev && \
    apt-get install -y zlib1g-dev && \
    apt-get install -y openssl libssl-dev

# Download and decompress Nginx
RUN mkdir -p /tmp/build/nginx && \
    cd /tmp/build/nginx && \
    wget -O ${NGINX_VERSION}.tar.gz https://nginx.org/download/${NGINX_VERSION}.tar.gz && \
    tar -zxf ${NGINX_VERSION}.tar.gz

#Install pip3
RUN apt-get install -y python3-pip 

#Install fast-api
RUN pip3 install fastapi[all] && \
    pip3 install gunicorn

#Install loguru
RUN pip3 install loguru

#Install nacos
RUN pip3 install nacos-sdk-python

#Install DBUtils
RUN pip3 install DBUtils && \
    pip3 install pymysql

# Download and decompress RTMP module
RUN mkdir -p /tmp/build/nginx-rtmp-module && \
    cd /tmp/build/nginx-rtmp-module && \
    wget -O nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION}.tar.gz https://github.com/arut/nginx-rtmp-module/archive/v${NGINX_RTMP_MODULE_VERSION}.tar.gz && \
    tar -zxf nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION}.tar.gz && \
    cd nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION}

# Build and install Nginx
# The default puts everything under /usr/local/nginx, so it's needed to change
# it explicitly. Not just for order but to have it in the PATH
RUN cd /tmp/build/nginx/${NGINX_VERSION} && \
    ./configure \
    --sbin-path=/usr/local/sbin/nginx \
    --conf-path=/etc/nginx/nginx.conf \
    --error-log-path=/var/log/nginx/error.log \
    --pid-path=/var/run/nginx/nginx.pid \
    --lock-path=/var/lock/nginx/nginx.lock \
    --http-log-path=/var/log/nginx/access.log \
    --http-client-body-temp-path=/tmp/nginx-client-body \
    --with-http_ssl_module \
    --with-threads \
    --with-ipv6 \
    --with-cc-opt="-Wimplicit-fallthrough=0" \
    --add-module=/tmp/build/nginx-rtmp-module/nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION} && \
    make -j $(getconf _NPROCESSORS_ONLN) && \
    make install && \
    mkdir /var/lock/nginx && \
    rm -rf /tmp/build

# Forward logs to Docker
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# Set up config file
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Config Stunnel
RUN mkdir -p  /etc/stunnel/conf.d

# Set up config file 
COPY stunnel/stunnel.conf /etc/stunnel/stunnel.conf
COPY stunnel/stunnel4 /etc/default/stunnel4

#ivs Stunnel Port 19351
COPY stunnel/ivs.conf /etc/stunnel/conf.d/ivs.conf

# Set up main file
COPY fastapi/ /
RUN pip3 install -r requirement.txt

#ivs
ENV IVS_URL rtmp://127.0.0.1:19351/rtmp/
ENV IVS_KEY ""

#nacos
ENV SERVER_ADDRESSES=http://knight-register:8848
ENV NAMESPACE=bigdata
ENV GROUP=DEFAULT_GROUP
ENV DATA_ID=common_config

#secondary_push_url
ENV SECONDARY_PUSH_URL ""

ENV DEBUG ""

COPY docker-entrypoint.sh /docker-entrypoint.sh

# RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash -
# RUN apt-get install -y nodejs
# COPY validation-server /etc/validation-server
# RUN cd /etc/validation-server && npm i

RUN chmod +x /docker-entrypoint.sh

EXPOSE 1935
EXPOSE 8000

ENTRYPOINT ["sh","/docker-entrypoint.sh"]

CMD nginx -g 'daemon off;' & gunicorn main:app --worker-class uvicorn.workers.UvicornWorker -w 1 --bind 0.0.0.0:8000 --access-logfile - 
# CMD nginx -g 'daemon off;' & node /etc/validation-server/index.js
