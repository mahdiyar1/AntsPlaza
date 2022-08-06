from .models import Strategy, StrategyExecution
# TODO think about runtime adds strategies
from .strategies.short_long import short_long
from .strategies import strategy
from .exchanges import *
import ccxt

# TODO whole check
class Engine:  # TODO think about make it object
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
        strategy_execution.is_long_closed = False
        strategy_execution.is_short_closed = False
        strategy_execution.leverage = 0
        strategy_execution.save()
        cls.strategies[strategy_id].run(strategy_execution.id)

    @classmethod
    def terminate(cls, strategy_id):
        cls.strategies[strategy_id].terminate()

    @classmethod
    def check_risk(cls, strategy_id):
        cls.strategies[strategy_id].check_risk()

    @staticmethod
    def create_exchange(information):
        exchange_id = information.api_information.exchange.id
        exchange_class_txt = 'ants_plaza_{exchange_id_txt}.AntsPlaza{exchange_id_txt}()'
        exchange_class = exchange_class_txt.format(exchange_id_txt=exchange_id)
        exchange: ccxt.Exchange = eval(exchange_class)
        exchange.apiKey = information.api_information.key
        exchange.secret = information.api_information.secret
        exchange.password = information.api_information.password
        exchange.instantiate_exchange_specific_client()
        return exchange

    @staticmethod
    def create_strategy(information, exchange: ccxt.Exchange):
        trader_id = information.trader.id
        strategy_id = information.id
        exchange_information = information.api_information.exchange
        strategy_class_txt = '{module}.{class_name}(exchange, trader_id, strategy_id, exchange_information)'
        strategy_class = strategy_class_txt.format(
            module=information.strategy_class.module, class_name=information.strategy_class.name)
        strategy = eval(strategy_class)
        return strategy
