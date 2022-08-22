from django.db import models
from engine.models import Trader


class MarginBalance(models.Model):
    currency = models.CharField(max_length=255)
    free = models.DecimalField(max_digits=24, decimal_places=12)
    used = models.DecimalField(max_digits=24, decimal_places=12)
    total = models.DecimalField(max_digits=24, decimal_places=12)
    trader = models.ForeignKey(Trader, on_delete=models.PROTECT)

# class ActiveStrategyStatistics(models.Model):

