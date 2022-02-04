import datetime
from random import shuffle
from typing import List

from tortoise import fields
from tortoise.models import Model


class MonthlySubmission(Model):
    id = fields.IntField(pk=True)
    token_name = fields.TextField()
    symbol = fields.TextField()
    date_submitted = fields.DateField(default=datetime.date.today())

    async def get_randomized_submissions(self, date_range: List[str]) -> List[Model]:
        submissions = await self.filter(
            date_submitted__range=date_range
        )
        shuffle(submissions)
        return submissions[:10]

    def __repr__(self):
        return f"<MonthlySubmissions: {self.token_name} ({self.symbol})>"

    def __str__(self):
        return f"{self.token_name} ({self.symbol})"
