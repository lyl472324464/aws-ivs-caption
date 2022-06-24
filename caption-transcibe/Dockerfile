FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN mkdir -p /caption
WORKDIR /caption
RUN apt-get update && \
    apt-get install -y ffmpeg python3-pip supervisor curl
RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs
# RUN apt-get install -y --allow-downgrades libssl1.1=1.1.1f-1ubuntu2
# RUN apt-get install -y npm
COPY . ./
RUN cd transcribe-server && \
    npm install --silent
RUN pip3 install -r requirement.txt
RUN chmod +x runapp.sh
ENV SERVER_ADDRESSES=knight-register:8848
ENV NAMESPACE=bigdata
ENV GROUP=DEFAULT_GROUP
ENV COMMON_CONFIG_DATA_ID=common_config
ENV SPECIAL_CONFIG_DATA_ID=live_caption
EXPOSE 8000
CMD ["sh","runapp.sh"]
