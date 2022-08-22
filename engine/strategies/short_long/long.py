import datetime
from ...models import Order, StrategyExecution
from .persistance import Persistence
from .helper import Helper


class Long():

    def __init__(self, strategy):
        self.strategy = strategy
        self.persistance: Persistence = strategy.persistance
        self.helper: Helper = strategy.helper

    def execute(self):
        symbol = self.helper.get_long_symbol()

        fund = self.helper.get_short_sell_order().cost_fee_adjusted

        fund_adjusted = self.helper.handle_order_min_and_precision(
            symbol, fund=fund)

        result = self.strategy.exchange.create_market_margin_order(
            symbol.id, 'buy', fund=fund_adjusted)

        self.handle_order_result(result)

        execution = StrategyExecution.objects.get(
            pk=self.strategy.execution_id)
        execution.is_long_success = True
        execution.long_buy_cost = Order.objects.filter(
            strategy_execution_id=self.strategy.execution_id, side='buy', position='long').first().cost_fee_adjusted
        execution.save()

    def cancel(self):
        symbol = self.helper.get_long_symbol()

        amount = self.helper.get_currency_balance(symbol.base)

        amount_adjusted = self.helper.handle_order_min_and_precision(
            symbol, amount=amount)

        result = self.strategy.exchange.create_market_margin_order(
            symbol.id, 'sell', 'test2', amount=amount_adjusted)  # TODO handle round currency and client order id and extract an function

        self.handle_order_result(result)
        execution = StrategyExecution.objects.get(
            pk=self.strategy.execution_id)
        execution.is_long_closed = True
        execution.long_sell_cost = self.helper.calculate_long_sell_total_cost()
        if execution.is_short_closed == True:
            execution.is_strategy_end = True
            execution.date_time_end = datetime.now()
        execution.save()

    def handle_order_result(self, result):
        order_id = result['orderId']
        order_result = self.helper.watch_and_fetch_result(
            self.strategy.exchange.fetch_order, order_id, 'closed', result_key_level_1='status')
        self.persistance.save_order(order_result, 'long')

    def sell_partial(self, fund_adjusted):
        symbol = self.helper.get_long_symbol()
        result = self.strategy.exchange.create_market_margin_order(
            symbol.id, 'sell', fund=fund_adjusted)

        self.handle_partial_result(result)

    def handle_partial_result(self, result):
        order_id = result['orderId']
        order_result = self.helper.watch_and_fetch_result(
            self.strategy.exchange.fetch_order, order_id, 'closed', result_key_level_1='status')  # TODO magic number
        self.persistance.save_order(
            order_result, 'long', is_fund_provide_order=True)
