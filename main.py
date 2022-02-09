import datetime
import logging
from operator import itemgetter

from discord import ApplicationContext, Interaction
from discord import Bot, Embed, ButtonStyle, AllowedMentions
from discord.commands import Option, permissions
from discord.ext.pages import Paginator, PaginatorButton
from discord.ui import View
from requests.exceptions import RequestException
from tortoise import Tortoise

from api.coingecko import CoinGecko
from api.coinmarketcap import CoinMarketCap
from button import ChartButton
from config import DISCORD_BOT_TOKEN, logger, DB_URL
from constants import KEYCAP_DIGITS
from models import MonthlySubmission
from utils import get_coin_ids, get_coin_stats, add_reactions

bot = Bot(allowed_mentions=AllowedMentions(everyone=True))


@bot.event
async def on_ready():
    logging.info(f"{bot.user} successfully logged in!")

    await Tortoise.init(db_url=DB_URL, modules={"models": ["models"]})
    await Tortoise.generate_schemas()


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
    paginator_buttons = [
        PaginatorButton(button_type="prev", label="", style=ButtonStyle.red, emoji="⬅"),
        PaginatorButton("page_indicator", style=ButtonStyle.gray, disabled=True),
        PaginatorButton(button_type="next", style=ButtonStyle.green, emoji="➡"),
    ]

    try:
        for ids in await get_coin_ids(symbol=symbol.upper()):
            coin_stats = await get_coin_stats(coin_id=ids)
            percent_change_24h, percent_change_7d, percent_change_30d = itemgetter(
                "percent_change_24h", "percent_change_7d", "percent_change_30d"
            )(coin_stats)

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
            embed_message.add_field(
                name="Price 💸", value=coin_stats["price"], inline=False
            )
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

        paginator = Paginator(
            pages=pages, use_default_buttons=False, custom_buttons=paginator_buttons
        )
        await paginator.respond(ctx.interaction)
    except TypeError as e:
        logger.error(e)
        await ctx.respond(
            embed=Embed(title=f"Data for ({symbol}) is not available", colour=0xC5E519)
        )
    except RequestException as e:
        logger.error(e)
        await ctx.respond(
            embed=Embed(
                title=f"Unable to get data for ({symbol}) at this time", colour=0xC5E519
            )
        )


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
    days: Option(
        str,
        "Number of days",
        choices=["1", "7", "14", "30", "90", "180", "365", "max"],
        required=True,
    ),
) -> None:
    """
    Displays token charting data
    :param ctx: Discord Bot Application Context
    :param symbol: Token Symbol
    :param days: Number of days to chart
    """
    logger.info("Price command executed")
    symbol = symbol.upper()
    embed_message = Embed(title="Choose chart to generate", colour=0x338E86)
    view = View(timeout=30)

    coin_ids = await get_coin_ids(symbol=symbol)

    for ids in coin_ids:
        view.add_item(item=ChartButton(label=ids, days=days, symbol=symbol))

    await ctx.respond(embed=embed_message, view=view)


@bot.slash_command()
async def submit_token(
    ctx: ApplicationContext,
    token_name: Option(str, "Name of token"),
    symbol: Option(str, "Symbol of token"),
) -> None:
    """
    Submits token to monthly poll to vote for token of the month
    :param ctx: Discord Bot Application Context
    :param token_name: Name of token
    :param symbol: Symbol of token
    """
    today = datetime.date.today()
    logger.info(f"{ctx.user} executed [submit_token] command")

    await MonthlySubmission.create(token_name=token_name, symbol=symbol)

    logger.info("Token submission success")
    embed_message = Embed(
        title=f"Submitted **{token_name} ({symbol})** to {today.strftime('%B %Y')} drawing",
        colour=0xBAD330,
    )

    await ctx.respond(embed=embed_message)


@bot.slash_command(default_permission=False)
@permissions.has_role("Admin")
async def monthly_draw(ctx: ApplicationContext) -> None:
    """
    Creates poll so that users may vote for the token of the month
    :param ctx: Discord Bot Application Context
    """
    logger.info(f"{ctx.user} executed [submit_token] command")
    reactions = []
    tokens = ""
    today = datetime.date.today()
    embed_message = Embed(colour=0x0F3FE5)

    submissions = await MonthlySubmission().get_randomized_submissions(
        date_range=[str(today.replace(day=1)), str(today)]
    )

    for index in range(len(submissions)):
        tokens += f"{KEYCAP_DIGITS[index]} {submissions[index]}\n\n"
        reactions.append(KEYCAP_DIGITS[index])

    embed_message.add_field(
        name="Vote for the token of the month! 🗳️", value=tokens, inline=True
    )

    interaction: Interaction = await ctx.respond(
        content="@everyone", embed=embed_message
    )

    await add_reactions(interaction.channel.last_message, reactions)


bot.run(DISCORD_BOT_TOKEN)
