from datetime import datetime
from decimal import Decimal

from ..strategy import Strategy

from .persistance import Persistence
from .helper import Helper
from ...models import Order, StrategyExecution, StrategySetting, Borrow


class Short():

    def __init__(self, strategy):
        self.strategy: Strategy = strategy
        self.persistance: Persistence = strategy.persistance
        self.helper: Helper = strategy.helper

    def execute(self):
        symbol = self.helper.get_short_symbol()

        borrow_to_max_borrow_ratio = StrategySetting.objects.filter(
            strategy_id=self.strategy.strategy_id, name='borrow_to_max_borrow_ratio').first().value  # TODO design in a way that guaranty is available

        max_borrow_amount = self.fetch_max_borrow_amount(
            symbol.base)

        order_amount = borrow_to_max_borrow_ratio * max_borrow_amount

        order_amount_precision_adjusted = self.helper.handle_order_min_and_precision(
            symbol, amount=order_amount)

        result = self.strategy.exchange.create_market_margin_order(
            symbol.id, 'sell', 'test', amount=order_amount_precision_adjusted, autoBorrow=True)  # TODO handle clientId ('test') AND float/decimal/precession

        self.handle_execute_result(result)

        execution = StrategyExecution.objects.get(
            pk=self.strategy.execution_id)
        execution.is_short_success = True
        execution.short_sell_cost = Order.objects.filter(
            strategy_execution_id=self.strategy.execution_id, side='sell', position='short').first().cost_fee_adjusted
        execution.save()

    def cancel(self):
        symbol = self.helper.get_short_symbol()

        borrow_order = self.helper.get_borrow_order()

        interest = borrow_order.interest

        sell_amount = self.helper.get_short_sell_order().amount

        buy_amount = sell_amount + interest

        buy_amount_adjusted = self.helper.handle_order_min_and_precision(
            symbol, amount=buy_amount, round_direction='up')

        result = self.strategy.exchange.create_market_margin_order(
            symbol.id, 'buy', amount=buy_amount_adjusted)

        self.handle_cancel_result(result)

        repay_amount = self.refund_for_cancel(symbol, borrow_order, interest)

        repay_amount_adjusted = self.helper.handle_order_min_and_precision(
            symbol, repay_amount, round_direction='up')

        repayment_result = self.strategy.exchange.repay_margin(
            symbol.base, 'RECENTLY_EXPIRE_FIRST', repay_amount_adjusted)

        self.handle_repayment_result(repayment_result)

        execution = StrategyExecution.objects.get(
            pk=self.strategy.execution_id)
        execution.is_short_closed = True
        execution.short_buy_cost = self.helper.calculate_short_buy_total_costs()
        if execution.is_long_closed == True or not execution.is_long_success:
            execution.is_strategy_end = True
            execution.date_time_end = datetime.now()

        execution.save()

    def handle_execute_result(self, result):
        borrow_order_id = result['loanApplyId']
        borrow_order_result = self.helper.watch_and_fetch_result(
            self.strategy.exchange.fetch_borrow_order, borrow_order_id, 'DONE', 'data', 'status', 0.3)  # TODO magic number
        self.persistance.save_borrow_order(borrow_order_result['data'])

        sell_order_id = result['orderId']
        sell_order_result = self.helper.watch_and_fetch_result(
            self.strategy.exchange.fetch_order, sell_order_id, 'closed', result_key_level_1='status', delay=0.3)  # TODO magic number
        self.persistance.save_order(sell_order_result, 'short')

    def handle_cancel_result(self, result):
        order_id = result['orderId']
        order_result = self.helper.watch_and_fetch_result(
            self.strategy.exchange.fetch_order, order_id, 'closed', result_key_level_1='status', delay=0.3)  # TODO magic number
        self.persistance.save_order(order_result, 'short')

    def handle_repayment_result(self, result):
        if result['code'] == '200000':
            borrow = self.helper.get_borrow_order()
            borrow.status = 'closed'
            borrow.save()

    def fetch_max_borrow_amount(self, currency):
        margin_balances = self.strategy.exchange.fetch_margin_balance()[
            'data']['accounts']
        for balance in margin_balances:
            if balance['currency'] == currency:
                return Decimal(balance['maxBorrowSize'])

    def refund_for_cancel(self, symbol, borrow_order, interest):
        repay_amount = borrow_order.amount + interest

        base_balance = self.helper.get_currency_balance(symbol.base)

        insufficient_base_balance = repay_amount - base_balance

        symbol_rate_fee = self.helper.get_fee_rate(symbol)

        while insufficient_base_balance > 0:
            last_price = Decimal(
                self.strategy.exchange.fetch_ticker(symbol.id)['last'])

            fund = insufficient_base_balance * last_price
            fund_needed = fund + fund * symbol_rate_fee

            quote_balance = self.helper.get_currency_balance(symbol.quote)

            insufficient_quote_balance = fund_needed - quote_balance
            insufficient_quote_balance_precision_adjusted = self.helper.handle_order_min_and_precision(
                self.helper.get_long_symbol(), fund=insufficient_quote_balance, round_direction='up')

            self.strategy.long.sell_partial(
                insufficient_quote_balance_precision_adjusted)

            insufficient_base_balance_precision_adjusted = self.helper.handle_order_min_and_precision(
                symbol, amount=insufficient_base_balance, round_direction='up')

            result = self.strategy.exchange.create_market_margin_order(
                symbol.id, 'buy', 'test3', amount=insufficient_base_balance_precision_adjusted)

            self.handle_cancel_result(result)

            base_balance = self.helper.get_currency_balance(symbol.base)
            insufficient_base_balance = repay_amount - base_balance

        return repay_amount
