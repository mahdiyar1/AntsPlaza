from datetime import datetime
from dateutil import parser
from decimal import Decimal
from ...models import Borrow, Order


class Persistence():

    def __init__(self, strategy):
        self.strategy = strategy

    def save_borrow_order(self, result):
        borrow = Borrow()
        borrow.id = result['orderId']
        borrow.amount = Decimal(result['filled'])
        borrow.currency = result['currency']
        borrow.datetime = datetime.now()
        borrow.strategy_id = self.strategy.strategy_id
        borrow.strategy_execution_id = self.strategy.execution_id
        borrow.trader_id = self.strategy.trader_id
        borrow.status = 'open'
        # TODO handle multiply borrow trade
        borrow.daily_interest_rate = result['matchList'][0]['dailyIntRate']
        borrow.interest = borrow.amount * Decimal(borrow.daily_interest_rate)
        borrow.save()

    def save_order(self, result, position, is_fund_provide_order=False):
        order = Order()
        order.amount = Decimal(result['amount'])
        order.average = Decimal(result['average'])
        order.client_order_id = result['clientOrderId']
        order.cost = result['cost']
        order.datetime = parser.parse(result['datetime'])
        order.filled = result['filled']
        order.id = result['id']
        order.price = result['price']
        order.remaining = result['remaining']
        order.side = result['side']
        order.strategy_execution_id = self.strategy.execution_id
        order.strategy_id = self.strategy.strategy_id
        order.symbol_id = self.handle_exchange_symbol_separator(
            result['symbol'])
        order.time_in_force = result['timeInForce']
        order.status = result['status']
        order.timestamp = result['timestamp']
        order.type = result['type']
        order.trader_id = self.strategy.trader_id
        order.fee = result['fee']['cost']
        order.position = position
        if order.side == 'buy':
            order.average_price_fee_included = Decimal(
                order.cost + order.fee) / order.amount
            order.cost_fee_adjusted = order.cost + order.fee
        else:
            order.average_price_fee_included = Decimal(
                order.cost - order.fee) / order.amount
            order.cost_fee_adjusted = order.cost - order.fee
        order.is_fund_provide_order = is_fund_provide_order
        order.save()

    def handle_exchange_symbol_separator(self, symbol: str):
        exchange_symbol_separator = self.strategy.exchange_information.symbol_separator
        return symbol.replace('/', exchange_symbol_separator)
