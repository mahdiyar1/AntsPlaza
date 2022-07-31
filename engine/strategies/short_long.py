from ..models import Borrow, Order, StrategySetting, StrategySymbol
from .strategy import Strategy
import ccxt
from kucoin.client import Margin, Trade
from dateutil import parser
from datetime import datetime
from decimal import Decimal
from pprint import pprint


class ShortLong(Strategy):

    def __init__(self, exchange: ccxt.Exchange, trader_id, strategy_id, exchange_information):
        super().__init__(exchange, trader_id, strategy_id, exchange_information)
        self.kucoin_margin = Margin(
            key=self.exchange.apiKey, secret=self.exchange.secret, passphrase=self.exchange.password)
        self.kucoin_trade = Trade(
            key=self.exchange.apiKey, secret=self.exchange.secret, passphrase=self.exchange.password)
        self.short_order_id = ''
        self.long_order_id = ''
        self.borrow_order_id = ''

    def run(self, execution_id):
        self.execution_id = execution_id
        self.execute_short()
        self.execute_long()

    def execute_short(self):
        short_symbol = StrategySymbol.objects.select_related('symbol').filter(
            strategy_id=self.strategy_id, side='sell').first().symbol

        balance_to_borrow_ratio = StrategySetting.objects.filter(
            strategy_id=self.strategy_id, name='balance_to_borrow_ratio').first().value

        borrow_size = self.get_max_borrow_size(
            short_symbol.base) * balance_to_borrow_ratio  # TODO handle ratio meaning

        short_result = self.kucoin_trade.create_market_margin_order(
            short_symbol.id, 'sell', 'test', autoBorrow=True, size=float(borrow_size))  # TODO handle clientId ('test') AND float/decimal/precession

        self.handle_short_result(short_result)

    def execute_long(self):
        long_symbol = StrategySymbol.objects.select_related('symbol').filter(
            strategy_id=self.strategy_id, side='buy').first().symbol

        long_size = Order.objects.get(pk=self.short_order_id).cost

        long_result = self.kucoin_trade.create_market_margin_order(
            long_symbol.id, 'buy', 'test1', funds=round(float(long_size), 1)) #TODO handle round usdt

        self.handle_long_result(long_result)

    def handle_short_result(self, result):
        borrow_order_id = result['loanApplyId']
        self.borrow_order_id = borrow_order_id
        borrow_order_result = self.exchange.fetch_borrow_order(borrow_order_id)
        self.save_borrow_order(borrow_order_result['data'])

        short_order_id = result['orderId']
        self.short_order_id = short_order_id
        short_order_result = self.exchange.fetch_order(short_order_id)
        self.save_order(short_order_result)

    def handle_long_result(self, result):
        long_order_id = result['orderId']
        self.long_order_id = long_order_id
        long_order_result = self.exchange.fetch_order(
            long_order_id)
        self.save_order(long_order_result)

    def save_borrow_order(self, result):
        loan = Borrow()
        loan.amount = Decimal(result['filled'])
        loan.currency = result['currency']
        loan.datetime = datetime.now()
        loan.strategy_id = self.strategy_id
        loan.strategy_execution_id = self.execution_id
        loan.trader_id = self.trader_id
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
        order.strategy_execution_id = self.execution_id
        order.strategy_id = self.strategy_id
        result['symbol']
        order.symbol_id = self.handle_exchange_symbol_separator(
            result['symbol'])
        order.time_in_force = result['timeInForce']
        order.status = result['status']
        order.timestamp = result['timestamp']
        order.type = result['type']
        order.trader_id = self.trader_id
        order.fee = result['fee']['cost']
        order.save()

    def get_max_borrow_size(self, currency):
        margin_balances = self.exchange.fetch_margin_balance()[
            'data']['accounts']
        for balance in margin_balances:
            if balance['currency'] == currency:
                return Decimal(balance['maxBorrowSize'])

    def check_risk(self):
        pass

    def handle_exchange_symbol_separator(self, symbol: str):
        exchange_symbol_separator = self.exchange_information.symbol_separator
        return symbol.replace('/', exchange_symbol_separator)

    def set_default_state(self):
        self.short_order_id = ''
        self.long_order_id = ''
        self.borrow_order_id = ''