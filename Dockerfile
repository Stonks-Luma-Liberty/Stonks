FROM python:3.8.12-buster

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH='/Stonks'

WORKDIR /Stonks
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /Stonks
