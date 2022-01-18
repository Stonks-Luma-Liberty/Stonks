import logging
import tempfile
from io import BufferedReader, BytesIO

import discord
import plotly.graph_objects as go
import plotly.io as pio
from discord import ApplicationContext
from discord import Bot, Embed, ButtonStyle
from discord.commands import Option
from discord.ext.pages import Paginator, PaginatorButton
from inflection import humanize

from api.coingecko import CoinGecko
from api.coinmarketcap import CoinMarketCap
from config import DISCORD_BOT_TOKEN, logger
from utils import get_coin_ids, get_coin_stats

bot = Bot()


@bot.event
async def on_ready():
    logging.info(f"{bot.user} successfully logged in!")


@bot.slash_command()
async def price(
    ctx: ApplicationContext, symbol: Option(str, "Enter token symbol")
) -> None:
    """
    Displays token price data from CoinGecko/CoinMarketCap
    :param ctx: Discord Bot Application Context
    :param symbol: Cryptocurrency token symbol
    """
    logger.info("Price command executed")
    pages = []
    coin_ids = await get_coin_ids(symbol=symbol.upper())

    for ids in coin_ids:
        coin_stats = await get_coin_stats(coin_id=ids)
        percent_change_24h = coin_stats["percent_change_24h"]
        percent_change_7d = coin_stats["percent_change_7d"]
        percent_change_30d = coin_stats["percent_change_30d"]

        embed_message = Embed(
            title=f"{coin_stats['name']} ({coin_stats['symbol']})",
            url=coin_stats["website"],
            colour=0xC5E519,
        )
        embed_message.add_field(
            name="Explorers 🔗",
            value=", ".join(coin_stats["explorers"]),
            inline=False,
        )
        embed_message.add_field(name="Price 💸", value=coin_stats["price"], inline=False)
        embed_message.add_field(
            name="Market Cap Rank 🥇",
            value=coin_stats["market_cap_rank"],
            inline=False,
        )
        embed_message.add_field(
            name="Market Cap 🏦", value=coin_stats["market_cap"], inline=False
        )
        embed_message.add_field(
            name="Volume 💰", value=coin_stats["volume"], inline=False
        )
        embed_message.add_field(
            name="24H Change 📈" if percent_change_24h > 0 else "24H Change 📉",
            value=f"{percent_change_24h}%",
            inline=False,
        )
        embed_message.add_field(
            name="7D Change 📈" if percent_change_7d > 0 else "7D Change 📉",
            value=f"{percent_change_7d}%",
            inline=True,
        )
        embed_message.add_field(
            name="30D Change 📈" if percent_change_30d > 0 else "30D Change 📉",
            value=f"{percent_change_30d}%",
            inline=True,
        )

        if "percent_change_ath" in coin_stats:
            percent_change_ath = coin_stats["percent_change_ath"]
            embed_message.add_field(
                name="ATH Change 📈" if percent_change_ath > 0 else "ATH Change 📉",
                value=f"{percent_change_ath}%",
                inline=True,
            )
        pages.append(embed_message)
    paginator = Paginator(pages=pages, use_default_buttons=False)
    paginator.add_button(
        PaginatorButton(button_type="prev", label="", style=ButtonStyle.red, emoji="⬅")
    )
    paginator.add_button(
        PaginatorButton("page_indicator", style=ButtonStyle.gray, disabled=True)
    )
    paginator.add_button(
        PaginatorButton(button_type="next", style=ButtonStyle.green, emoji="➡")
    )
    await paginator.respond(ctx.interaction)


@bot.slash_command()
async def trending(ctx: ApplicationContext) -> None:
    """
    Displays trending tokens on CoinGecko & CoinMarketCap
    :param ctx: Discord Bot Application Context
    """
    logger.info("Retrieving trending addresses from CoinGecko")
    coin_gecko = CoinGecko()
    coin_market_cap = CoinMarketCap()

    coin_gecko_trending_coins = "\n> ".join(await coin_gecko.get_trending_coins())
    coin_market_cap_trending_coins = "\n> ".join(
        await coin_market_cap.get_trending_coins()
    )

    embed_message = Embed(title="Trending tokens 🔥", colour=0x43CA7E)
    embed_message.add_field(
        name="CoinGecko", value=f"> {coin_gecko_trending_coins}", inline=False
    )
    embed_message.add_field(
        name="CoinMarketCap", value=f"> {coin_market_cap_trending_coins}", inline=False
    )
    await ctx.respond(embed=embed_message)


@bot.slash_command()
async def chart(
    ctx: ApplicationContext,
    symbol: Option(str, "Symbol of token to chart"),
    days: Option(str, "Number of days", choices=["1", "7", "14", "30", "90", "180", "365", "max"], required=True),
):
    logger.info("Price command executed")
    coin_gecko = CoinGecko()
    symbol = symbol.upper()

    coin_ids = await get_coin_ids(symbol=symbol)

    for ids in coin_ids:
        market = await coin_gecko.coin_market_lookup(
            ids=ids, time_frame=days, base_coin="usd"
        )
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=market.Date,
                    open=market.Open,
                    high=market.High,
                    low=market.Low,
                    close=market.Close,
                ),
            ]
        )
        fig.update_layout(
            title=f"Candlestick graph for {humanize(ids)} ({symbol})",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False,
        )

        fig.update_yaxes(tickprefix="$")

        await ctx.respond(
            file=discord.File(
                BufferedReader(
                    BytesIO(pio.to_image(fig, format="png", engine="kaleido"))  # type: ignore
                ),
                filename=f"{tempfile.NamedTemporaryFile()}.png",
            )
        )


bot.run(DISCORD_BOT_TOKEN)
