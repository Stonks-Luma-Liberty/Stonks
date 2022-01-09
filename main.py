import logging

import discord

from config import DISCORD_BOT_TOKEN

# Initialize Bot and Denote The Command Prefix
bot = discord.Bot()


# Runs when Bot Successfully Connects

@bot.event
async def on_ready():
    logging.info(f'{bot.user} successfully logged in!')


@bot.slash_command()
async def price(ctx, symbol: str):  # The name of the function is the name of the command
    await ctx.reply(f"This is a test. Symbol received = {symbol}")
    # await ctx.send(f"This is a test. Symbol received = {symbol}")  # ctx.send sends text in chat


bot.run(DISCORD_BOT_TOKEN)
