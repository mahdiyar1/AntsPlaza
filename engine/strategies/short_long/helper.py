import time
from decimal import Decimal
from math import ceil, floor
from ...models import Borrow, Order, StrategyExecution, StrategySymbol, Symbol


class Helper():

    def __init__(self, strategy):
        self.strategy = strategy

    def get_short_symbol(self):
        strategy_execution_task_id = StrategyExecution.objects.filter(
            pk=self.strategy.execution_id).first().task_id
        symbol = StrategySymbol.objects.select_related('symbol').filter(
            strategy_id=self.strategy.strategy_id, position='short',
            strategy_execution_task_id=strategy_execution_task_id).first().symbol
        
        return symbol

    def get_long_symbol(self):
        strategy_execution_task_id = StrategyExecution.objects.filter(
            pk=self.strategy.execution_id).first().task_id
        symbol = StrategySymbol.objects.select_related('symbol').filter(
            strategy_id=self.strategy.strategy_id, position='long',
            strategy_execution_task_id=strategy_execution_task_id).first().symbol

        return symbol
        
    def get_short_sell_order(self):
        return Order.objects.filter(strategy_execution_id=self.strategy.execution_id, position='short', side='sell').first()

    def get_long_buy_order(self):
        return Order.objects.filter(strategy_execution_id=self.strategy.execution_id, position='long', side='buy').first()

    def get_borrow_order(self):
        return Borrow.objects.filter(strategy_execution_id=self.strategy.execution_id).first()

    def get_fee_rate(self, symbol):
        return Symbol.objects.get(pk=symbol.id).maker_fee_rate

    def handle_order_min_and_precision(self, symbol, amount=None, fund=None, round_direction='down'):
        if fund:
            min_fund = Symbol.objects.get(pk=symbol.id).market_order_min_fund
            if min_fund > fund:
                return float(min_fund)
            precision = Symbol.objects.get(
                pk=symbol.id).market_order_precision_fund
            if round_direction == 'down':
                fund = floor(fund * pow(10, precision)) / \
                    float(pow(10, precision))
                return fund
            fund = ceil(fund * pow(10, precision)) / \
                float(pow(10, precision))
            return fund

        # if amount
        min_amount = Symbol.objects.get(pk=symbol.id).base_min_amount
        if min_amount > amount:
            return float(min_amount)
        precision = Symbol.objects.get(pk=symbol.id).base_precision
        if round_direction == 'down':
            amount = floor(amount * pow(10, precision)) / \
                float(pow(10, precision))
            return amount
        amount = ceil(amount * pow(10, precision)) / float(pow(10, precision))
        return amount

    def watch_and_fetch_result(self, method, argument, condition, result_key_level_1=None, result_key_level_2=None, delay=0):
        result = None

        while result != condition:
            if result:
                time.sleep(delay)
            original_result = method(argument)
            result = original_result
            if result_key_level_1 and result:
                result = result.get(result_key_level_1)
            if result_key_level_2 and result:
                result = result.get(result_key_level_2)

        return original_result

    def get_currency_balance(self, currency):
        margin_balances = self.strategy.exchange.fetch_margin_balance()[
            'data']['accounts']
        for balance in margin_balances:
            if balance['currency'] == currency:
                return Decimal(balance['availableBalance'])

    def calculate_short_buy_total_costs(self):
        total_cost = 0
        orders = Order.objects.filter(
            strategy_execution_id=self.strategy.execution_id, side='buy', position='short')
        for order in orders:
            total_cost = total_cost + order.cost_fee_adjusted

        return total_cost

    def calculate_long_sell_total_cost(self):
        total_cost = 0
        orders = Order.objects.filter(
            strategy_execution_id=self.strategy.execution_id, side='sell', position='long')
        for order in orders:
            total_cost = total_cost + order.cost_fee_adjusted

        return total_cost
