from django.conf import settings
from django.db import models

# TODO organized it


class Trader(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    telephone_number = models.CharField(max_length=255, null=True)
    telegram_username = models.CharField(max_length=255, null=True)


class Exchange(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    timeout = models.IntegerField()
    rate_limit = models.IntegerField()
    symbol_separator = models.CharField(max_length=255)


class ApiInformation(models.Model):
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    trader = models.ForeignKey(Trader, on_delete=models.PROTECT)
    exchange = models.ForeignKey(Exchange, on_delete=models.PROTECT)


class StrategyClass(models.Model):
    name = models.CharField(max_length=255)
    module = models.CharField(max_length=255)


class Strategy(models.Model):
    strategy_class = models.ForeignKey(StrategyClass, on_delete=models.PROTECT)
    trader = models.ForeignKey(Trader, on_delete=models.PROTECT)
    api_information = models.ForeignKey(
        ApiInformation, on_delete=models.PROTECT)
    active = models.BooleanField()


class StrategySetting(models.Model):
    name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=24, decimal_places=12)
    comment = models.CharField(max_length=255)
    strategy = models.ForeignKey(Strategy, on_delete=models.PROTECT)


class StrategyExecution(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.PROTECT)
    date_time_begin = models.DateTimeField(auto_now_add=True)
    date_time_end = models.DateTimeField(null=True)
    state = models.CharField(max_length=255)
    is_short_closed = models.BooleanField()
    is_long_closed = models.BooleanField()
    leverage  = models.DecimalField(max_digits=24, decimal_places=12)
    last_short_return = models.DecimalField(max_digits=24, decimal_places=12, null=True)
    last_long_return = models.DecimalField(max_digits=24, decimal_places=12, null=True)


# TODO think about integration with binance
class Symbol(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    base = models.CharField(max_length=255)
    quote = models.CharField(max_length=255)
    base_min_amount = models.DecimalField(max_digits=24, decimal_places=12)
    base_precision = models.IntegerField()
    market_order_min_fund = models.DecimalField(
        max_digits=24, decimal_places=12)
    market_order_precision_fund = models.IntegerField()
    taker_fee_rate = models.DecimalField(
        max_digits=24, decimal_places=12)
    maker_fee_rate = models.DecimalField(
        max_digits=24, decimal_places=12)


class Order(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    client_order_id = models.CharField(max_length=255, null=True)
    trader = models.ForeignKey(Trader, on_delete=models.PROTECT)
    strategy = models.ForeignKey(Strategy, on_delete=models.PROTECT)
    symbol = models.ForeignKey(Symbol, on_delete=models.PROTECT)
    strategy_execution = models.ForeignKey(
        StrategyExecution, on_delete=models.PROTECT)
    datetime = models.DateTimeField()
    timestamp = models.BigIntegerField()
    status = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    time_in_force = models.CharField(max_length=255)
    side = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=24, decimal_places=12, null=True)
    average = models.DecimalField(max_digits=24, decimal_places=12, null=True)
    average_price_fee_included = models.DecimalField(
        max_digits=24, decimal_places=12, null=True)
    amount = models.DecimalField(max_digits=24, decimal_places=12)
    filled = models.DecimalField(max_digits=24, decimal_places=12)
    remaining = models.DecimalField(max_digits=24, decimal_places=12)
    cost = models.DecimalField(max_digits=24, decimal_places=12)
    cost_fee_adjusted = models.DecimalField(max_digits=24, decimal_places=12)
    fee = models.DecimalField(max_digits=24, decimal_places=12)
    is_fund_provide_order = models.BooleanField()


class Trade(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    trader = models.ForeignKey(Trader, on_delete=models.PROTECT)
    strategy = models.ForeignKey(Strategy, on_delete=models.PROTECT)
    strategy_execution = models.ForeignKey(
        StrategyExecution, on_delete=models.PROTECT)
    datetime = models.DateTimeField()
    timestamp = models.BigIntegerField()
    symbol = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    side = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=24, decimal_places=12, null=True)
    taker_or_maker = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=24, decimal_places=12)
    cost = models.DecimalField(max_digits=24, decimal_places=12)


class MarginBalance(models.Model):
    currency = models.CharField(max_length=255)
    free = models.DecimalField(max_digits=24, decimal_places=12)
    used = models.DecimalField(max_digits=24, decimal_places=12)
    total = models.DecimalField(max_digits=24, decimal_places=12)
    trader = models.ForeignKey(Trader, on_delete=models.PROTECT)


class Borrow(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    trader = models.ForeignKey(Trader, on_delete=models.PROTECT)
    strategy = models.ForeignKey(Strategy, on_delete=models.PROTECT)
    strategy_execution = models.ForeignKey(
        StrategyExecution, on_delete=models.PROTECT)
    currency = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=24, decimal_places=12)
    datetime = models.DateTimeField()
    daily_interest_rate = models.DecimalField(max_digits=24, decimal_places=12)
    status = models.CharField(max_length=255)
    interest = models.DecimalField(max_digits=24, decimal_places=12)


class currency(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    code = models.CharField(max_length=255)


class StrategySymbol(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.PROTECT)
    position = models.CharField(max_length=255)
    strategy = models.ForeignKey(Strategy, on_delete=models.PROTECT)
