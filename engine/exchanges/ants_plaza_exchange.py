from abc import abstractclassmethod


class AntsPlazaExchange():

    @abstractclassmethod
    def instantiate_exchange_specific_client(self):
        pass

    @abstractclassmethod
    def fetch_margin_balance(self):
        pass

    @abstractclassmethod
    def fetch_borrow_order(self, order_id):
        pass

    @abstractclassmethod
    def create_market_margin_order(
            self, symbol, side, auto_borrow, clientOid='', **kwargs):
        pass

    @abstractclassmethod
    def repay_margin(self, currency, sequence, size):
        pass

    @abstractclassmethod
    def fetch_symbols(self):
        pass