import ccxt
from .persistance import Persistence
from .short import Short
from .long import Long
from .risk import Risk
from .helper import Helper
from ...strategies import strategy
from ...models import StrategyExecution, StrategySetting, Strategy


class ShortLong(strategy.Strategy):

    def __init__(self, exchange: ccxt.Exchange, trader_id, strategy_id, exchange_information):
        super().__init__(exchange, trader_id, strategy_id, exchange_information)
        # must be first of instantiate list because below classes use it
        self.persistance = Persistence(self)
        self.helper = Helper(self)
        self.short = Short(self)
        self.long = Long(self)
        self.risk = Risk(self)

    def run_short(self, execution_id):
        self.execution_id = execution_id
        self.save_execution_leverage()
        strategy_execution = StrategyExecution.objects.get(
            pk=self.execution_id)
        strategy_execution.short_symbol = self.helper.get_short_symbol()
        strategy_execution.long_symbol = self.helper.get_long_symbol()
        strategy_execution.save()
        self.short.execute()

    def run_long(self):
        strategy = Strategy.objects.select_related(
            'last_strategy_execution').filter(pk=self.strategy_id).first()
        if strategy.last_strategy_execution_id:
            execution = strategy.last_strategy_execution
            if not execution.is_long_success and (execution.is_short_success and not execution.is_short_closed):
                self.long.execute()

    def terminate_short(self):
        strategy = Strategy.objects.select_related(
            'last_strategy_execution').filter(pk=self.strategy_id).first()
        if strategy.last_strategy_execution_id:
            execution = strategy.last_strategy_execution
            if execution.is_short_success and not execution.is_short_closed:
                self.short.cancel()

    def terminate_long(self):
        strategy = Strategy.objects.select_related(
            'last_strategy_execution').filter(pk=self.strategy_id).first()
        if strategy.last_strategy_execution_id:
            execution = strategy.last_strategy_execution
            if execution.is_long_success and not execution.is_long_closed:
                self.long.cancel()

    def check_risk(self):
        strategy = Strategy.objects.select_related(
            'last_strategy_execution').filter(pk=self.strategy_id).first()
        if not strategy.last_strategy_execution_id:
            return

        execution = strategy.last_strategy_execution
        short_return_ratio = 0
        long_return_ratio = 0

        if execution.is_short_success and not execution.is_short_closed:
            if execution.is_short_closed:
                short_return_ratio = execution.last_short_return
            else:
                short_data = self.risk.short()
                short_return_ratio = short_data[0]
                execution.last_short_return_ratio = short_return_ratio
                execution.last_short_return = short_data[1]
                execution.save()

        if execution.is_long_success and not execution.is_long_closed:
            if execution.is_long_closed:
                long_return_ratio = execution.last_long_return
            else:
                long_data = self.risk.long()
                long_return_ratio = long_data[0]
                execution.last_long_return_ratio = long_return_ratio
                execution.last_long_return = long_data[1]
                execution.save()

        if (execution.is_short_success and not execution.is_short_closed) or (execution.is_short_success and not execution.is_long_closed):
            self.risk.portfolio(short_return_ratio, long_return_ratio)

    def terminate(self):
        self.terminate_long()
        self.terminate_short()

    def save_execution_leverage(self):
        execution = StrategyExecution.objects.get(pk=self.execution_id)

        borrow_to_max_borrow_ratio = StrategySetting.objects.filter(
            strategy_id=self.strategy_id, name='borrow_to_max_borrow_ratio').first().value
        account_leverage = StrategySetting.objects.filter(
            strategy_id=self.strategy_id, name='account_leverage').first().value

        self.leverage = borrow_to_max_borrow_ratio * account_leverage
        execution.leverage = self.leverage
        execution.save()

    def fetch_symbols(self):
        symbols = self.exchange.fetch_symbols()['data']
