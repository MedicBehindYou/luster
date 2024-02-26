FROM debian:latest

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3

RUN pip install -U pip numpy scipy matplotlib pandas seaborn configparser requests --break-system-packages

COPY . /app

RUN mkdir /config && mkdir /app/downloads && mv config.ini /config/config.ini

RUN chmod 777 * -R && cd /config && chmod 777 * -R

ENTRYPOINT ["/bin/bash"]