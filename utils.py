from http.client import HTTPException
from operator import itemgetter
from typing import List, Dict, Any
from urllib.error import HTTPError
from urllib.parse import urlparse

from discord import Embed, Interaction

from api.coingecko import CoinGecko
from api.coinmarketcap import CoinMarketCap
from config import logger


def get_coin_explorers(platforms: dict, links: dict) -> list:
    """
    Locate token explorers and stores them in a list.

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
    Retrieve coin IDs from supported market aggregators.

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


async def get_coin_stats(coin_id: str) -> Dict[str, Any]:
    """Retrieve coin stats from connected services crypto services.

    Args:
        coin_id (str): ID of coin to lookup in cryptocurrency market aggregators

    Returns:
        dict: Cryptocurrency coin statistics
    """
    # Search with CoinGecko API
    logger.info(f"Getting coin stats for {coin_id}")
    coin_gecko = CoinGecko()
    coin_stats: Dict[str, Any] = {}
    price, all_time_high, market_cap, volume = "0", "0", "0", "0"
    try:
        token_data = await coin_gecko.coin_lookup(ids=coin_id)

        market_data, links, platforms = itemgetter("market_data", "links", "platforms")(
            token_data
        )
        (
            percent_change_24h,
            percent_change_7d,
            percent_change_30d,
            market_cap_rank,
        ) = itemgetter(
            "price_change_percentage_24h",
            "price_change_percentage_7d",
            "price_change_percentage_30d",
            "market_cap_rank",
        )(
            market_data
        )
        percent_change_ath = market_data["ath_change_percentage"]["usd"]
        explorers = get_coin_explorers(platforms=platforms, links=links)

        if "usd" in market_data["current_price"]:
            price = f"${float(market_data['current_price']['usd']):,}"
            all_time_high = f"${float(market_data['ath']['usd']):,}"
            market_cap = f"${float(market_data['market_cap']['usd']):,}"
            volume = f"${float(market_data['total_volume']['usd']):,}"

        coin_stats.update(
            {
                "name": token_data["name"],
                "symbol": token_data["symbol"].upper(),
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
        # Search with CoinMarketCap API
        logger.info(
            f"{coin_id} not found in CoinGecko. Initiated lookup on CoinMarketCap."
        )
        coin_market_cap = CoinMarketCap()
        ids = coin_id[0]
        coin_lookup = coin_market_cap.coin_lookup(ids=ids)
        meta_data = coin_market_cap.get_coin_metadata(ids=ids)[ids]
        token_data = coin_lookup[ids]
        urls = meta_data["urls"]
        quote = token_data["quote"]["USD"]
        explorers = [
            f"[{urlparse(link).hostname.split('.')[0]}]({link})"
            for link in urls["explorer"]
            if link
        ]

        price = f"${quote['price']:,}"
        market_cap = f"${quote['market_cap']:,}"
        volume = f"${quote['volume_24h']:,}"
        percent_change_24h = quote["percent_change_24h"]
        percent_change_7d = quote["percent_change_7d"]
        percent_change_30d = quote["percent_change_30d"]

        coin_stats.update(
            {
                "name": token_data["name"],
                "symbol": token_data["symbol"],
                "website": urls["website"][0],
                "explorers": explorers,
                "price": price,
                "market_cap_rank": token_data["cmc_rank"],
                "market_cap": market_cap,
                "volume": volume,
                "percent_change_24h": percent_change_24h or 0,
                "percent_change_7d": percent_change_7d or 0,
                "percent_change_30d": percent_change_30d or 0,
            }
        )

    return coin_stats


async def add_reactions(message: Interaction, reactions: List[str]) -> None:
    """
    Add reactions to a message.

    :param message: The message to add reactions to
    :type message: Interaction
    :param reactions: A list of reactions to add to the message
    :type reactions: List[str]
    """
    for reaction in reactions:
        await message.add_reaction(reaction)


def generate_price_embed(token_data: dict) -> Embed:
    """
    Generate Discord embed message used in price command.

    :param token_data: Token data
    :return: Discord embed message
    """
    logger.info("Generating price data discord embed")
    percent_change_24h, percent_change_7d, percent_change_30d = itemgetter(
        "percent_change_24h", "percent_change_7d", "percent_change_30d"
    )(token_data)

    embed_message = Embed(
        title=f"{token_data['name']} ({token_data['symbol']})",
        url=token_data["website"],
        colour=0xC5E519,
    )
    fields = [
        ("Explorers 🔗", ", ".join(token_data["explorers"]), False),
        ("Price 💸", token_data["price"], False),
        ("Market Cap Rank 🥇", token_data["market_cap_rank"], False),
        ("Volume 💰", token_data["volume"], False),
        (
            "24H Change 📈" if percent_change_24h > 0 else "24H Change 📉",
            f"{percent_change_24h}%",
            False,
        ),
        (
            "7D Change 📈" if percent_change_7d > 0 else "7D Change 📉",
            f"{percent_change_7d}%",
            True,
        ),
        (
            "30D Change 📈" if percent_change_30d > 0 else "30D Change 📉",
            f"{percent_change_30d}%",
            True,
        ),
    ]

    if "percent_change_ath" in token_data:
        percent_change_ath = token_data["percent_change_ath"]
        fields.append(
            (
                "ATH Change 📈" if percent_change_ath > 0 else "ATH Change 📉",
                f"{percent_change_ath}%",
                True,
            )
        )

    for field in fields:
        embed_message.add_field(name=field[0], value=field[1], inline=field[2])
    return embed_message
