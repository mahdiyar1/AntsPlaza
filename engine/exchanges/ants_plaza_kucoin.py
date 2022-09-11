from ccxt import kucoin
from kucoin.client import Margin, Trade
from .ants_plaza_exchange import AntsPlazaExchange


class AntsPlazakucoin(kucoin, AntsPlazaExchange):

    def __init__(self, config={}):
        super().__init__(config)
        self.margin_client = None
        self.trade_client = None

    def instantiate_exchange_specific_client(self):
        self.margin_client = Margin(
            key=self.apiKey, secret=self.secret, passphrase=self.password)

        self.trade_client = Trade(
            key=self.apiKey, secret=self.secret, passphrase=self.password)

    def fetch_margin_balance(self):
        return self.private_get_margin_account()

    def fetch_borrow_order(self, order_id):
        return self.private_get_margin_borrow({'orderId': order_id})

    def create_market_margin_order(
            self, symbol, side, clientOid='', **kwargs):

        amount = kwargs.get('amount')
        if amount:
            del kwargs['amount']
            kwargs['size'] = amount

        fund = kwargs.get('fund')
        if fund:
            del kwargs['fund']
            kwargs['funds'] = fund

        return self.trade_client.create_market_margin_order(
            symbol, side, clientOid, **kwargs)

    def repay_margin(self, currency, sequence, amount):
        return self.margin_client.click_to_repayment(currency, sequence, amount)

    def fetch_symbols(self):
        return self.public_get_symbols()