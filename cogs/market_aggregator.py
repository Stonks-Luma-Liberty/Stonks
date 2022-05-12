from discord import slash_command, ApplicationContext, ButtonStyle, Embed, option
from discord.ext.commands import Cog
from discord.ext.pages import Paginator, PaginatorButton
from discord.ui import View
from requests.exceptions import RequestException

from api.coingecko import CoinGecko
from api.coinmarketcap import CoinMarketCap
from button import ChartButton
from config import logger, DISCORD_GUILD_GUIDS
from utils import get_coin_ids, get_coin_stats, generate_price_embed


class MarketAggregator(Cog):
    def __init__(self, bot):
        """
        Initialize market aggregator bot.

        :param bot: Discord bot
        """
        self.bot = bot

    @slash_command(guild_ids=DISCORD_GUILD_GUIDS)
    @option(name="symbol", description="Enter token symbol", required=True)
    async def price(self, ctx: ApplicationContext, symbol: str) -> None:
        """
        Display token price data from CoinGecko/CoinMarketCap.

        :param ctx: Discord Bot Application Context
        :param symbol: Cryptocurrency token symbol
        """
        logger.info("Price command executed")
        pages = []

        await ctx.defer()

        try:
            for ids in await get_coin_ids(symbol=symbol.upper()):
                coin_stats = await get_coin_stats(coin_id=ids)
                embed_message = generate_price_embed(token_data=coin_stats)
                pages.append(embed_message)

            paginator = Paginator(
                pages=pages,
                use_default_buttons=False,
                custom_buttons=[
                    PaginatorButton(
                        button_type="prev", label="", style=ButtonStyle.red, emoji="⬅"
                    ),
                    PaginatorButton(
                        "page_indicator", style=ButtonStyle.gray, disabled=True
                    ),
                    PaginatorButton(
                        button_type="next", style=ButtonStyle.green, emoji="➡"
                    ),
                ],
            )
            await paginator.respond(ctx.interaction)
        except TypeError as error:
            logger.error(error)
            await ctx.respond(
                embed=Embed(
                    title=f"Data for ({symbol}) is not available", colour=0xC5E519
                )
            )
        except RequestException as error:
            logger.error(error)
            await ctx.respond(
                embed=Embed(
                    title=f"Unable to get data for ({symbol}) at this time",
                    colour=0xC5E519,
                )
            )

    @slash_command(guild_ids=DISCORD_GUILD_GUIDS)
    async def trending(self, ctx: ApplicationContext) -> None:
        """
        Display trending tokens on CoinGecko & CoinMarketCap.

        :param ctx: Discord Bot Application Context
        """
        logger.info("Retrieving trending addresses from CoinGecko")
        coin_gecko = CoinGecko()
        coin_market_cap = CoinMarketCap()
        embed_message = Embed(title="Trending tokens 🔥", colour=0x43CA7E)

        await ctx.defer()

        coin_gecko_trending_coins = "\n> ".join(await coin_gecko.get_trending_coins())
        coin_market_cap_trending_coins = "\n> ".join(
            await coin_market_cap.get_trending_coins()
        )

        try:
            embed_message.add_field(
                name="CoinGecko", value=f"> {coin_gecko_trending_coins}", inline=False
            )
            embed_message.add_field(
                name="CoinMarketCap",
                value=f"> {coin_market_cap_trending_coins}",
                inline=False,
            )
        except RequestException as error:
            logger.error(error)
            embed_message.title = "Unable to get trending tokens at this time"
        await ctx.respond(embed=embed_message)

    @slash_command(guild_ids=DISCORD_GUILD_GUIDS)
    @option(name="symbol", description="Enter symbol of token to chart", required=True)
    @option(
        name="days",
        description="Choose number of days to plot",
        choices=["1", "7", "14", "30", "90", "180", "365", "max"],
        required=True,
    )
    async def chart(
        self,
        ctx: ApplicationContext,
        symbol: str,
        days: str,
    ) -> None:
        """
        Display token charting data.

        :param ctx: Discord Bot Application Context
        :param symbol: Token Symbol
        :param days: Number of days to chart
        """
        logger.info("Price command executed")
        symbol = symbol.upper()
        embed_message = Embed(title="Choose chart to generate", colour=0x338E86)
        view = View(timeout=30)

        await ctx.defer()

        try:
            coin_ids = await get_coin_ids(symbol=symbol)

            for ids in coin_ids:
                view.add_item(item=ChartButton(label=ids, days=days, symbol=symbol))

        except RequestException as error:
            logger.error(error)
            embed_message.title = "Unable to gather charting data at this moment"
        await ctx.respond(embed=embed_message, view=view)
