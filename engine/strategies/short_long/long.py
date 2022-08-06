from ...models import StrategyExecution
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
            symbol.id, 'buy', 'test1', fund=fund_adjusted)  # TODO handle client order id

        self.handle_order_result(result)

    def cancel(self):
        symbol = self.helper.get_long_symbol()

        amount = self.helper.get_currency_balance(symbol.base)

        amount_adjusted = self.helper.handle_order_min_and_precision(
            symbol, amount=amount)

        result = self.strategy.exchange.create_market_margin_order(
            symbol.id, 'sell', 'test2', amount=amount_adjusted)  # TODO handle round currency and client order id and extract an function

        self.handle_order_result(result)
        #TODO return success or not
        execution = StrategyExecution.objects.get(pk=self.strategy.execution_id)
        execution.is_long_closed = True
        execution.save()

    def handle_order_result(self, result):
        # TODO handle errors
        order_id = result['orderId']
        order_result = self.helper.watch_and_fetch_result(
            self.strategy.exchange.fetch_order, order_id, 'closed', 0.3, 'status')  # TODO magic number
        self.persistance.save_order(order_result, 'long')

    def sell_partial(self, fund_adjusted):
        symbol = self.helper.get_long_symbol()
        result = self.strategy.exchange.create_market_margin_order(
            symbol.id, 'sell', 'test1', fund=fund_adjusted)  # TODO handle round usdt and client order id

        self.handle_partial_result(result)

    def handle_partial_result(self,result):
        order_id = result['orderId']
        order_result = self.helper.watch_and_fetch_result(
            self.strategy.exchange.fetch_order, order_id, 'closed', 0.3, 'status')  # TODO magic number
        self.persistance.save_order(order_result, 'long', is_fund_provide_order=True)

