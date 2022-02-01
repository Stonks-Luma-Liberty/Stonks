from aiocoingecko import AsyncCoinGeckoAPISession
from pandas import DataFrame, to_datetime
from requests.exceptions import RequestException

from api import coingecko_coin_lookup_cache
from config import logger


class CoinGecko:
    def __init__(self):
        self.cg = AsyncCoinGeckoAPISession()

    async def coin_lookup(self, ids: str, is_address: bool = False) -> dict:
        """Coin lookup in CoinGecko API

        Args:
            ids (str): id of coin to lookup
            is_address (bool): Indicates if given ids is a crypto address

        Returns:
            dict: Data from CoinGecko API
        """
        logger.info("Looking up price for %s in CoinGecko API", ids)
        async with self.cg as cg:
            try:
                data = (
                    await cg.get_coin_info_from_contract_address_by_id(
                        platform_id="ethereum", contract_address=ids
                    )
                    if is_address
                    else await cg.get_coin_by_id(coin_id=ids)
                )
            except ValueError:
                data = await cg.get_coin_info_from_contract_address_by_id(
                    platform_id="binance-smart-chain", contract_address=ids
                )
            except RequestException:
                data = (
                    await cg.get_coin_info_from_contract_address_by_id(
                        platfomr_id="binance", contract_address=ids
                    )
                    if is_address
                    else await cg.get_coin_by_id(coin_id=ids)
                )
        return data

    async def get_trending_coins(self) -> list:
        """
        Gets trending coins
        Returns (list): Trending coins

        """
        logger.info("Retrieving CoinGecko trending coins")

        async with self.cg as cg:
            trending_coins = await cg.get_search_trending()
        return [
            f"{coin['item']['name']} ({coin['item']['symbol']})"
            for coin in trending_coins["coins"]
        ]

    async def coin_market_lookup(
        self, ids: str, time_frame: str, base_coin: str
    ) -> DataFrame:
        """Coin lookup in CoinGecko API for Market Chart

        Args:
            ids (str): id of coin to lookup
            time_frame (str): Indicates number of days for data span
            base_coin (str): Indicates base coin

        Returns:
            dict: Data from CoinGecko API
        """
        logger.info("Looking up chart data for %s in CoinGecko API", ids)

        async with self.cg as cg:
            data = await cg.get_coin_ohlc_by_id(
                coin_id=ids, vs_currency=base_coin, days=time_frame
            )
            dataframe = DataFrame(
                data, columns=["Date", "Open", "High", "Low", "Close"]
            )
            dataframe.Date = to_datetime(dataframe.Date, unit="ms")
            return dataframe

    async def get_coin_ids(self, symbol: str) -> list:
        """Retrieves coin stats from connected services crypto services

        Args:
            symbol (str): Cryptocurrency symbol of coin to lookup

        Returns:
            list: coin ids of matching search results for given symbol
        """
        logger.info("Getting coin ID for %s", symbol)
        coin_ids = []

        if symbol in coingecko_coin_lookup_cache.keys():
            coin_ids.append(coingecko_coin_lookup_cache[symbol])
        else:
            async with self.cg as cg:
                coins = [
                    coin
                    for coin in await cg.get_coins_list()
                    if coin["symbol"].upper() == symbol
                ]

            for coin in coins:
                coin_id = coin["id"]
                coin_ids.append(coin_id)

            if len(coin_ids) == 1:
                coingecko_coin_lookup_cache[symbol] = coin_ids[0]

        return coin_ids
