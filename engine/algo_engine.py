import ccxt
from .models import Strategy, StrategyExecution
from .strategies.short_long import short_long  # dont delete this import
from .strategies import strategy  # dont delete this import
from .exchanges import *


class Engine:
    strategies = {}

    @classmethod
    def init(cls):
        strategies_information = Strategy.objects.select_related(
            'strategy_class', 'api_information__exchange', 'last_strategy_execution').filter(active=True)
        for information in strategies_information:
            exchange = cls.create_exchange(information)
            strategy = cls.create_strategy(information, exchange)
            strategy_id = information.id
            if information.last_strategy_execution_id:
                execution = information.last_strategy_execution
                if not execution.is_strategy_end:
                    strategy.execution_id = execution.id
                    strategy.leverage = execution.leverage
            cls.strategies[strategy_id] = strategy

    @classmethod
    def run_short(cls, strategy_id, strategy_execution_task_id):
        strategy = Strategy.objects.select_related(
            'last_strategy_execution').filter(pk=strategy_id).first()
        if strategy.last_strategy_execution_id:
            execution = strategy.last_strategy_execution
            if not execution.is_strategy_end:
                return
        strategy_execution = StrategyExecution()
        strategy_execution.strategy_id = strategy_id
        strategy_execution.is_long_closed = False
        strategy_execution.is_short_closed = False
        strategy_execution.is_long_success = False
        strategy_execution.is_short_success = False
        strategy_execution.is_strategy_end = False
        strategy_execution.leverage = 0
        strategy_execution.task_id = strategy_execution_task_id
        strategy_execution.save()
        strategy.last_strategy_execution_id = strategy_execution.id
        strategy.save()
        cls.strategies[strategy_id].run_short(strategy_execution.id)

    @classmethod
    def run_long(cls, strategy_id):
        cls.strategies[strategy_id].run_long()

    @classmethod
    def run_short_all(cls, strategy_execution_task_id):
        for strategy_id in cls.strategies.keys():
            cls.run_short(strategy_id, strategy_execution_task_id)

    @classmethod
    def run_long_all(cls):
        for strategy_id in cls.strategies.keys():
            cls.run_long(strategy_id)

    @classmethod
    def terminate_short(cls, strategy_id):
        cls.strategies[strategy_id].terminate_short()

    @classmethod
    def terminate_long(cls, strategy_id):
        cls.strategies[strategy_id].terminate_long()

    @classmethod
    def terminate_short_all(cls):
        for strategy_id in cls.strategies.keys():
            cls.terminate_short(strategy_id)

    @classmethod
    def terminate_long_all(cls):
        for strategy_id in cls.strategies.keys():
            cls.terminate_long(strategy_id)

    @classmethod
    def terminate(cls, strategy_id):
        cls.strategies[strategy_id].terminate()

    @classmethod
    def terminate_all(cls):
        for strategy_id in cls.strategies.keys():
            cls.terminate(strategy_id)

    @classmethod
    def check_risk(cls, strategy_id):
        cls.strategies[strategy_id].check_risk()

    @classmethod
    def check_risk_all(cls):
        for strategy_id in cls.strategies.keys():
            cls.check_risk(strategy_id)

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
