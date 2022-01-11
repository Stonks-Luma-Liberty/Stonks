import logging

from discord import ApplicationContext
from discord import Bot, Embed, ButtonStyle
from discord.ext.pages import Paginator, PaginatorButton

from config import DISCORD_BOT_TOKEN, logger
from utils import get_coin_ids, get_coin_stats

bot = Bot()


@bot.event
async def on_ready():
    logging.info(f"{bot.user} successfully logged in!")


@bot.slash_command()
async def price(ctx: ApplicationContext, symbol: str):
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
                name="ATH Change 📈" if percent_change_ath else "ATH Change 📉",
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


bot.run(DISCORD_BOT_TOKEN)
