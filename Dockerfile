FROM debian:latest

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3

RUN pip install -U pip numpy scipy matplotlib pandas seaborn configparser requests --break-system-packages

COPY . /app

RUN mkdir /config && mkdir /app/downloads

RUN chmod 777 /app/ -R && chmod 777 /config/ -R

ENTRYPOINT ["python3", "-u", "/app/main.py"]