FROM python:3.10.4-slim-bullseye
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH='/Stonks'
COPY . /Stonks
WORKDIR /Stonks
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential libssl-dev pkg-config patchelf \
    && apt-get clean && rm -rf /var/lib/apt/lists/* && curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

