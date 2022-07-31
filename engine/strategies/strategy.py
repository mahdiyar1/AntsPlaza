import ccxt
import abc


class Strategy:

    def __init__(self, exchange: ccxt.Exchange, trader_id, strategy_id, exchange_information):
        self.exchange = exchange
        self.trader_id = trader_id
        self.strategy_id = strategy_id
        self.execution_id = 0
        self.exchange_information = exchange_information

    @abc.abstractmethod
    def run(self, execution_id):
        pass

    @abc.abstractmethod
    def check_risk(self):
        pass
