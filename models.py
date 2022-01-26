import datetime

from tortoise import fields
from tortoise.models import Model


class MonthlySubmission(Model):
    id = fields.IntField(pk=True)
    token_name = fields.TextField()
    symbol = fields.TextField()
    date_submitted = fields.DateField(default=datetime.date.today())

    def __repr__(self):
        return f"<MonthlySubmissions: {self.token_name} ({self.symbol})>"

    def __str__(self):
        return f"{self.token_name} ({self.symbol})"
