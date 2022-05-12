import logging

from discord import Bot, AllowedMentions
from tortoise import Tortoise

from cogs.market_aggregator import MarketAggregator
from cogs.monthly_draw import MonthlyDraw
from config import DISCORD_BOT_TOKEN, DB_URL

bot = Bot(allowed_mentions=AllowedMentions(everyone=True))


@bot.event
async def on_ready() -> None:
    """Initialize discord bot."""
    logging.info(f"{bot.user} successfully logged in!")

    await Tortoise.init(db_url=DB_URL, modules={"models": ["models"]})
    await Tortoise.generate_schemas()


if __name__ == "__main__":
    bot.add_cog(MarketAggregator(bot))
    bot.add_cog(MonthlyDraw(bot))
    bot.run(DISCORD_BOT_TOKEN)
