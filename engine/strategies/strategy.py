import ccxt
import abc


class Strategy:

    def __init__(self, exchange, trader_id, strategy_id, exchange_information):
        self.exchange = exchange
        self.trader_id = trader_id
        self.strategy_id = strategy_id        
        self.exchange_information = exchange_information
        self.execution_id = None
        self.leverage = None

    @abc.abstractmethod
    def check_risk(self):
        pass

    @abc.abstractmethod
    def terminate(self):
        pass
