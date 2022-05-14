import datetime

from discord import (
    slash_command,
    ApplicationContext,
    Embed,
    default_permissions,
    Interaction,
    option,
)
from discord.ext.commands import Cog
from tortoise.exceptions import BaseORMException

from config import DISCORD_GUILD_GUIDS, logger
from constants import KEYCAP_DIGITS
from models import MonthlySubmission
from utils import add_reactions


class MonthlyDraw(Cog):
    def __init__(self, bot):
        """
        Initialize monthly draw cog.

        :param bot: Discord bot
        """
        self.bot = bot

    @slash_command(guild_ids=DISCORD_GUILD_GUIDS)
    @option(name="token_name", description="Enter token name", required=True)
    @option(name="symbol", description="Enter token symbol", required=True)
    @option(
        name="description",
        description="Enter alpha as to why this token should be bought",
        required=True,
    )
    async def submit_token(
        self, ctx: ApplicationContext, token_name: str, symbol: str, description: str
    ) -> None:
        """
        Submit token to monthly poll to vote for token of the month.

        :param ctx: Discord Bot Application Context
        :param token_name: Name of token
        :param symbol: Symbol of token
        """
        today = datetime.date.today()
        logger.info("%s executed [submit_token] command", ctx.user)
        title = (
            f"Submitted {token_name} ({symbol}) to {today.strftime('%B %Y')} drawing"
        )
        embed_message = Embed(
            title=title,
            colour=0xBAD330,
        )

        await ctx.defer()

        try:
            await MonthlySubmission.create(
                token_name=token_name, symbol=symbol, description=description
            )
            logger.info("Token submission success")
        except BaseORMException as error:
            logger.error(error)
            embed_message.title("Unable to submit token at this time. Try again later")

        await ctx.respond(embed=embed_message)

    @slash_command(guild_ids=DISCORD_GUILD_GUIDS, default_permission=False)
    @default_permissions(administrator=True)
    async def monthly_draw(self, ctx: ApplicationContext) -> None:
        """
        Create poll so that users may vote for the token of the month.

        :param ctx: Discord Bot Application Context
        """
        logger.info("%s executed [submit_token] command", ctx.user)
        reactions = []
        today = datetime.date.today()
        embed_message = Embed(
            colour=0x0F3FE5, title="Vote for the token of the month! 🗳️"
        )

        await ctx.defer()

        try:
            submissions = await MonthlySubmission().get_randomized_submissions(
                date_range=[str(today.replace(day=1)), str(today)]
            )

            for index, submission in enumerate(submissions):
                reaction = KEYCAP_DIGITS[index]
                embed_message.add_field(
                    name=f"{reaction} {submission}",
                    value=submission.description,
                    inline=False,
                )
                reactions.append(reaction)

            interaction: Interaction = await ctx.respond(
                content="@everyone", embed=embed_message
            )

            await add_reactions(interaction.channel.last_message, reactions)
        except BaseORMException as error:
            logger.error(error)
            embed_message.clear_fields()
            embed_message.title = "Unable to draw at this moment. Try again later"
            await ctx.respond(embed=embed_message)
