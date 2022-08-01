import ccxt
from kucoin.client import Margin, Trade
from dateutil import parser
from datetime import datetime
from decimal import Decimal
from pprint import pprint
from ..models import Borrow, Order, StrategySetting, StrategySymbol
from .strategy import Strategy


class ShortLong(Strategy):

    def __init__(self, exchange: ccxt.Exchange, trader_id, strategy_id, exchange_information):
        # TODO think about exchange_specific instead of kucoin
        super().__init__(exchange, trader_id, strategy_id, exchange_information)
        self.kucoin_margin = Margin(
            key=self.exchange.apiKey, secret=self.exchange.secret, passphrase=self.exchange.password)
        self.kucoin_trade = Trade(
            key=self.exchange.apiKey, secret=self.exchange.secret, passphrase=self.exchange.password)
        # TODO create dic instead of string
        self.short_order_id = ''
        self.long_order_id = ''
        self.borrow_order_id = ''
        self.persistance = Persistence(self)
        self.short = Short(self)
        self.long = Long(self)

    def run(self, execution_id):
        self.execution_id = execution_id
        self.set_default_state()
        self.short.execute_short()
        self.long.execute_long()

    def check_risk(self):
        pass

    def terminate(self):
        pass

    def set_default_state(self):
        self.short_order_id = ''
        self.long_order_id = ''
        self.borrow_order_id = ''


class Short():

    def __init__(self, strategy: ShortLong):
        self.strategy = strategy
        self.persistance = strategy.persistance

    def execute_short(self):
        short_symbol = StrategySymbol.objects.select_related('symbol').filter(
            strategy_id=self.strategy.strategy_id, side='sell').first().symbol

        balance_to_borrow_ratio = StrategySetting.objects.filter(
            strategy_id=self.strategy.strategy_id, name='balance_to_borrow_ratio').first().value

        borrow_size = self.get_max_borrow_size(
            short_symbol.base) * balance_to_borrow_ratio  # TODO handle ratio meaning

        short_result = self.strategy.kucoin_trade.create_market_margin_order(
            short_symbol.id, 'sell', 'test', autoBorrow=True, size=float(borrow_size))  # TODO handle clientId ('test') AND float/decimal/precession

        self.handle_short_result(short_result)

    def handle_short_result(self, result):
        borrow_order_id = result['loanApplyId']
        self.strategy.borrow_order_id = borrow_order_id
        borrow_order_result = self.strategy.exchange.fetch_borrow_order(
            borrow_order_id)
        self.persistance.save_borrow_order(borrow_order_result['data'])

        short_order_id = result['orderId']
        self.strategy.short_order_id = short_order_id
        short_order_result = self.strategy.exchange.fetch_order(short_order_id)
        self.persistance.save_order(short_order_result)

    def get_max_borrow_size(self, currency):
        margin_balances = self.strategy.exchange.fetch_margin_balance()[
            'data']['accounts']
        for balance in margin_balances:
            if balance['currency'] == currency:
                return Decimal(balance['maxBorrowSize'])


class Long():

    def __init__(self, strategy: ShortLong):
        self.strategy = strategy
        self.persistance = strategy.persistance

    def execute_long(self):
        long_symbol = StrategySymbol.objects.select_related('symbol').filter(
            strategy_id=self.strategy.strategy_id, side='buy').first().symbol

        long_size = Order.objects.get(pk=self.strategy.short_order_id).cost

        long_result = self.strategy.kucoin_trade.create_market_margin_order(
            long_symbol.id, 'buy', 'test1', funds=round(float(long_size), 1))  # TODO handle round usdt

        self.handle_long_result(long_result)

    def handle_long_result(self, result):
        long_order_id = result['orderId']
        self.strategy.long_order_id = long_order_id
        long_order_result = self.strategy.exchange.fetch_order(
            long_order_id)
        self.persistance.save_order(long_order_result)


class Persistence():

    def __init__(self, strategy):
        self.strategy = strategy

    def save_borrow_order(self, result):
        loan = Borrow()
        loan.amount = Decimal(result['filled'])
        loan.currency = result['currency']
        loan.datetime = datetime.now()
        loan.strategy_id = self.strategy.strategy_id
        loan.strategy_execution_id = self.strategy.execution_id
        loan.trader_id = self.strategy.trader_id
        loan.status = 'open'
        loan.daily_interest_rate = result['matchList'][0]['dailyIntRate']
        loan.save()

    def save_order(self, result):
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
        result['symbol']
        order.symbol_id = self.handle_exchange_symbol_separator(
            result['symbol'])
        order.time_in_force = result['timeInForce']
        order.status = result['status']
        order.timestamp = result['timestamp']
        order.type = result['type']
        order.trader_id = self.strategy.trader_id
        order.fee = result['fee']['cost']
        order.save()

    def handle_exchange_symbol_separator(self, symbol: str):
        exchange_symbol_separator = self.strategy.exchange_information.symbol_separator
        return symbol.replace('/', exchange_symbol_separator)
