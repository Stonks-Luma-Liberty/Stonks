from http.client import HTTPException
from typing import List
from urllib.error import HTTPError
from urllib.parse import urlparse

from discord import Message

from api.coingecko import CoinGecko
from api.coinmarketcap import CoinMarketCap
from config import logger


def get_coin_explorers(platforms: dict, links: dict) -> list:
    """
    Locates token explorers and stores them in a list
    Args:
        platforms (dict): Chains where token is available
        links (dict): Blockchain sites

    Returns (list): List of all available explorers

    """
    explorers = [
        f"[{urlparse(link).hostname.split('.')[0]}]({link})"
        for link in links["blockchain_site"]
        if link
    ]

    for network, address in platforms.items():
        explorer = ""

        if "ethereum" in network:
            explorer = f"[etherscan](https://etherscan.io/token/{address})"
        elif "binance" in network:
            explorer = f"[bscscan](https://bscscan.com/token/{address})"
        elif "polygon" in network:
            explorer = f"[polygonscan](https://polygonscan.com/token/{address})"
        elif "solana" in network:
            explorer = (
                f"[explorer.solana](https://explorer.solana.com/address/{address})"
            )

        if explorer and explorer not in explorers:
            explorers.append(explorer)
    return explorers


async def get_coin_ids(symbol: str) -> list:
    """
    Retrieves coin IDs from supported market aggregators
    Args:
        symbol: Token symbol

    Returns: List of matching symbols

    """
    coin_gecko = CoinGecko()
    coin_market_cap = CoinMarketCap()
    try:
        coin_ids = await coin_gecko.get_coin_ids(symbol=symbol)
    except (IndexError, HTTPError):
        coin_ids = coin_market_cap.get_coin_ids(symbol=symbol)
    return coin_ids


async def get_coin_stats(coin_id: str) -> dict:
    """Retrieves coin stats from connected services crypto services

    Args:
        coin_id (str): ID of coin to lookup in cryptocurrency market aggregators

    Returns:
        dict: Cryptocurrency coin statistics
    """
    logger.info(f"Getting coin stats for {coin_id}")
    # Search CoinGecko API first
    coin_gecko = CoinGecko()
    coin_market_cap = CoinMarketCap()
    coin_stats = {}
    price, all_time_high, market_cap, volume = 0, 0, 0, 0
    try:
        data = await coin_gecko.coin_lookup(ids=coin_id)

        market_data = data["market_data"]
        links = data["links"]
        platforms = data["platforms"]

        explorers = get_coin_explorers(platforms=platforms, links=links)

        if "usd" in market_data["current_price"]:
            price = "${:,}".format(float(market_data["current_price"]["usd"]))
            all_time_high = "${:,}".format(float(market_data["ath"]["usd"]))
            market_cap = "${:,}".format(float(market_data["market_cap"]["usd"]))
            volume = "${:,}".format(float(market_data["total_volume"]["usd"]))

        percent_change_24h = market_data["price_change_percentage_24h"]
        percent_change_7d = market_data["price_change_percentage_7d"]
        percent_change_30d = market_data["price_change_percentage_30d"]
        percent_change_ath = market_data["ath_change_percentage"]["usd"]
        market_cap_rank = market_data["market_cap_rank"]

        coin_stats.update(
            {
                "name": data["name"],
                "symbol": data["symbol"].upper(),
                "website": links["homepage"][0],
                "explorers": explorers,
                "price": price,
                "ath": all_time_high,
                "market_cap_rank": market_cap_rank,
                "market_cap": market_cap,
                "volume": volume,
                "percent_change_24h": percent_change_24h or 0,
                "percent_change_7d": percent_change_7d or 0,
                "percent_change_30d": percent_change_30d or 0,
                "percent_change_ath": percent_change_ath or 0,
            }
        )

    except (IndexError, HTTPError, HTTPException):
        logger.info(
            f"{coin_id} not found in CoinGecko. Initiated lookup on CoinMarketCap."
        )
        ids = coin_id[0]
        coin_lookup = coin_market_cap.coin_lookup(ids=ids)
        meta_data = coin_market_cap.get_coin_metadata(ids=ids)[ids]
        data = coin_lookup[ids]
        urls = meta_data["urls"]
        quote = data["quote"]["USD"]
        explorers = [
            f"[{urlparse(link).hostname.split('.')[0]}]({link})"
            for link in urls["explorer"]
            if link
        ]

        for key in quote:
            if quote[key] is None:
                quote[key] = 0
        price = "${:,}".format(quote["price"])
        market_cap = "${:,}".format(quote["market_cap"])
        volume = "${:,}".format(quote["volume_24h"])
        percent_change_24h = quote["percent_change_24h"]
        percent_change_7d = quote["percent_change_7d"]
        percent_change_30d = quote["percent_change_30d"]

        coin_stats.update(
            {
                "name": data["name"],
                "symbol": data["symbol"],
                "website": urls["website"][0],
                "explorers": explorers,
                "price": price,
                "market_cap_rank": data["cmc_rank"],
                "market_cap": market_cap,
                "volume": volume,
                "percent_change_24h": percent_change_24h,
                "percent_change_7d": percent_change_7d,
                "percent_change_30d": percent_change_30d,
            }
        )
    return coin_stats


async def add_reactions(message: Message, reactions: List[str]) -> None:
    """
    Adds reactions to message
    :param message: Discord Message
    :param reactions: List of reactions to add to message
    """
    for reaction in reactions:
        await message.add_reaction(reaction)
