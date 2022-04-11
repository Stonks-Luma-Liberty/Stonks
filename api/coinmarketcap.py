from typing import Any

from coinmarketcap_utils.coinmarketcap_utils import get_trending_tokens
from coinmarketcapapi import CoinMarketCapAPI

from config import COIN_MARKET_CAP_API_KEY
from config import logger


class CoinMarketCap:
    def __init__(self):
        """Create CoinMarketCap API instance."""
        self.cmc = CoinMarketCapAPI(COIN_MARKET_CAP_API_KEY)

    def get_coin_ids(self, symbol: str) -> list:
        """
        Retrieve coin ids for matching symbol.

        Args:
            symbol (str): Token symbol

        Returns (list): List of token ids

        """
        logger.info("Looking up token ids for %s in CoinMarketCap API", symbol)
        return [
            (str(token["id"]), token["name"])
            for token in self.cmc.cryptocurrency_map(symbol=symbol).data
        ]

    def get_coin_metadata(self, ids: str) -> Any:
        """
        Retrieve coin metadata.

        Args:
            ids (str): Token id

        Returns (Any): Metadata for provided coin ids
        """
        return self.cmc.cryptocurrency_info(id=ids).data

    def coin_lookup(self, ids: str) -> Any:
        """Coin lookup in CoinMarketCap API.

        Args:
            ids (str): CoinMarketCap token ids

        Returns:
            Any: Results of coin lookup
        """
        logger.info("Looking up price for %s in CoinMarketCap API", ids)
        return self.cmc.cryptocurrency_quotes_latest(id=ids, convert="usd").data

    @staticmethod
    async def get_trending_coins() -> list:
        """
        Scalp trending coins from CoinMarketCap website.

        Returns (list): Trending coins

        """
        logger.info("Retrieving trending coins from CoinMarketCap")
        return get_trending_tokens()[:7]  # type: ignore
