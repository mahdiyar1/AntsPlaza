from .models import Strategy, StrategyExecution
from .strategies import *
from .exchanges import *
import ccxt


class Engine:
    strategies = {}

    @classmethod
    def init(cls):
        strategies_information = Strategy.objects.select_related(
            'strategy_class', 'api_information__exchange').filter(active=True)
        for information in strategies_information:
            exchange = cls.create_exchange(information)
            strategy = cls.create_strategy(information, exchange)
            strategy_id = information.id
            cls.strategies[strategy_id] = strategy

    @classmethod
    def run(cls, strategy_id):
        strategy_execution = StrategyExecution()
        strategy_execution.strategy_id = strategy_id
        strategy_execution.save()
        cls.strategies[strategy_id].run(strategy_execution.id)

    @classmethod
    def check_risk(cls, strategy_id):
        cls.strategies[strategy_id].check_risk()

    @staticmethod
    def create_exchange(strategy_information):
        exchange_id = strategy_information.api_information.exchange.id
        exchange_class_txt = 'ants_plaza_{exchange_id_txt}.AntsPlaza{exchange_id_txt}()'
        exchange_class = exchange_class_txt.format(exchange_id_txt = exchange_id)
        exchange: ccxt.Exchange = eval(exchange_class)
        exchange.apiKey = strategy_information.api_information.key
        exchange.secret = strategy_information.api_information.secret
        exchange.password = strategy_information.api_information.password
        return exchange

    @staticmethod
    def create_strategy(strategy_information, exchange: ccxt.Exchange) -> strategy.Strategy:
        trader_id = strategy_information.trader.id
        strategy_id = strategy_information.id
        exchange_information = strategy_information.api_information.exchange
        strategy_class_txt = '{module}.{class_name}(exchange, trader_id, strategy_id, exchange_information)'
        strategy_class = strategy_class_txt.format(
            module = strategy_information.strategy_class.module, class_name = strategy_information.strategy_class.name)
        strategy = eval(strategy_class)
        return strategy
