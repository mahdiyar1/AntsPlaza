import ccxt
from .persistance import Persistence
from .short import Short
from .long import Long
from .risk import Risk
from .helper import Helper
from ..strategy import Strategy
from ...models import StrategyExecution, StrategySetting


class ShortLong(Strategy):

    def __init__(self, exchange: ccxt.Exchange, trader_id, strategy_id, exchange_information):
        super().__init__(exchange, trader_id, strategy_id, exchange_information)
        # must be first of instantiate list because below classes use it
        self.persistance = Persistence(self)
        self.helper = Helper(self)
        self.short = Short(self)
        self.long = Long(self)
        self.risk = Risk(self)
        self.leverage = None

    def run(self, execution_id):
        self.execution_id = execution_id
        self.save_execution_leverage()
        # TODO handle when short dose not execute and about states that help maintain correct state of strategy
        self.short.execute()
        self.long.execute()

    def check_risk(self):
        execution = StrategyExecution.objects.get(pk=self.execution_id)

        if execution.is_short_closed:
            short_return_ratio = execution.last_short_return            
        else:
            short_return_ratio = self.risk.short()

        if execution.is_long_closed:
            long_return_ratio = execution.last_long_return    
        else:
            long_return_ratio = self.risk.long()

        if execution.is_short_closed and execution.is_long_closed:
            return

        self.risk.portfolio(short_return_ratio, long_return_ratio)

    def terminate(self):
        execution = StrategyExecution.objects.get(pk=self.execution_id)

        if not execution.is_long_closed:
            self.long.cancel()

        if not execution.is_short_closed:
            self.short.cancel()

    def save_execution_leverage(self):
        execution = StrategyExecution.objects.get(pk=self.execution_id)

        balance_to_borrow_ratio = StrategySetting.objects.filter(
            strategy_id=self.strategy_id, name='balance_to_borrow_ratio').first().value
        account_leverage = StrategySetting.objects.filter(
            strategy_id=self.strategy_id, name='account_leverage').first().value

        self.leverage = balance_to_borrow_ratio * account_leverage
        execution.leverage = self.leverage
        execution.save()
