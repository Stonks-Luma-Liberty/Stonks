FROM python:3.8.12-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH='/Stonks'

WORKDIR /Stonks
RUN apt-get update && apt-get -y upgrade && apt-get -y install libreadline-gplv2-dev libncursesw5-dev libssl-dev \
libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /Stonks
