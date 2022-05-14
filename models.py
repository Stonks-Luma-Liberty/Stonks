import datetime
from random import shuffle
from typing import List

from tortoise import fields
from tortoise.models import Model

from config import logger


class MonthlySubmission(Model):
    """MonthlySubmission database table ORM."""

    id = fields.IntField(pk=True)
    token_name = fields.TextField()
    description = fields.TextField()
    symbol = fields.TextField()
    date_submitted = fields.DateField(default=datetime.date.today())

    async def get_randomized_submissions(
        self, date_range: List[str]
    ) -> List["MonthlySubmission"]:
        """
        Retrieve up to 10 randomly picked submissions.

        :rtype: object
        :param date_range: Range between to dates to query the database
        :return: List of submissions
        """
        logger.info("Gathering poll submissions")
        submissions: List[MonthlySubmission] = await self.filter(
            date_submitted__range=date_range
        )
        shuffle(submissions)
        return submissions[:10]

    def __repr__(self):
        """

        Change model representation.

        :return: Model string repr
        """
        return f"<MonthlySubmissions: {self.token_name} ({self.symbol})>"

    def __str__(self):
        """
        Convert model to string.

        :return: Model as string
        """
        return f"{self.token_name} ({self.symbol})"
