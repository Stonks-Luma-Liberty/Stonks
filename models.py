import datetime
from random import shuffle
from typing import List

from tortoise import fields
from tortoise.models import Model

from config import logger


class MonthlySubmission(Model):
    id = fields.IntField(pk=True)
    token_name = fields.TextField()
    symbol = fields.TextField()
    date_submitted = fields.DateField(default=datetime.date.today())

    async def get_randomized_submissions(self, date_range: List[str]) -> List[Model]:
        """
        Retrieves submissions and shuffles them returning up to 10 submissions
        :param date_range: Range between to dates to query the database
        :return: List of submissions
        """
        logger.info("Gathering poll submissions")
        submissions = await self.filter(date_submitted__range=date_range)
        shuffle(submissions)
        return submissions[:10]

    def __repr__(self):
        return f"<MonthlySubmissions: {self.token_name} ({self.symbol})>"

    def __str__(self):
        return f"{self.token_name} ({self.symbol})"
