# Stonks

[![Github Issues](https://img.shields.io/github/issues/Stonks-Luma-Liberty/Stonks?logo=github&style=for-the-badge)](https://github.com/Stonks-Luma-Liberty/Stonks/issues)
[![Codacy Badge](https://img.shields.io/codacy/grade/16f181495daf491ba11557c00cc8c40f?logo=codacy&style=for-the-badge)](https://www.codacy.com/gh/Stonks-Luma-Liberty/Stonks/dashboard?utm_source=github.com&utm_medium=referral&utm_content=Stonks-Luma-Liberty/Stonks&utm_campaign=Badge_Grade)
[![Github Top Language](https://img.shields.io/github/languages/top/Stonks-Luma-Liberty/Stonks?logo=python&style=for-the-badge)](https://www.python.org)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg?style=for-the-badge)](https://github.com/wemake-services/wemake-python-styleguide)

Cryptocurrency data reporting bot. Extracts data from cryptocurrency market aggregators (CoinGecko/CoinMarketCap) and displays results via discord

## Table of Contents

- [Features](#features)

- [Environment Variables](#environment-variables)

- [Run Locally](#run-locally)

  - [With Docker](#with-docker)
  - [Without Docker](#without-docker)

## Features

- Display price data for cryptocurrencies available in CoinGecko/CoinMarketCap
- Display charting data for cryptocurrencies available in CoinGecko/CoinMarketCap
- Users may submit tokens to monthly drawing to then vote for the token they believe will perform the best
- Error handling
- Logging

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`DISCORD_BOT_TOKEN` - Token required to connect with your discord bot

`COIN_MARKET_CAP_API_KEY` - Token required to query CoinMarketCap for cryptocurrency market data

`DB_NAME` - Name of your database

`DB_HOST` - Host of your database

`DB_USER` - Database user

`DB_PASSWORD` - Database password for `DB_USER`

`DB_PORT` - Database port

## Run Locally

Clone the project

```bash
  git clone https://github.com/Stonks-Luma-Liberty/Stonks.git
```

Go to the project directory

```bash
  cd Stonks
```

Install maturin

```bash
pip install maturin
```

Build python rust module

```bash
maturin build -m coinmarketcap_utils/Cargo.toml -r -o coinmarketcap_utils/dist
```

### With Docker

Use docker-compose to start the bot

```bash
docker-compose up -d --build
```

### Without Docker

Install dependencies

```bash
  poetry install
```

Start the bot

```bash
  poetry run python main.py
```
