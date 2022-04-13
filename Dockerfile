FROM python:3.10.3-slim-bullseye
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH='/Stonks'
COPY . /Stonks
WORKDIR /Stonks
RUN apt-get update && apt-get -y upgrade && apt-get -y install git libncursesw5-dev libssl-dev \
libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev curl && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt

