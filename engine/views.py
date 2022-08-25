from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .algo_engine import Engine
from .models import Order, Strategy, StrategySetting, StrategySymbol, Symbol
from .serializers import OrderSerializer, PeriodicTaskSerializer, StrategySerializer, StrategySettingSerializer, StrategySymbolSerializer, SymbolSerializer
from .tasks import check_risk_all, run_long_all, run_short_all, terminate_all, terminate_long_all, terminate_short_all
from django_celery_beat.models import PeriodicTask


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class StrategySettingViewSet(ModelViewSet):
    queryset = StrategySetting.objects.all()
    serializer_class = StrategySettingSerializer


class StrategySymbolViewSet(ModelViewSet):
    queryset = StrategySymbol.objects.all()
    serializer_class = StrategySymbolSerializer


class SymbolViewSet(ModelViewSet):
    queryset = Symbol.objects.all()
    serializer_class = SymbolSerializer


class PeriodicTaskViewSet(ModelViewSet):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskSerializer


class StrategyViewSet(ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

@api_view()
def run_short_all_strategies(Request):
    # run_short_all.delay(20)
    Engine.run_short_all(20)
    return Response('ok')


@api_view()
def run_long_all_strategies(Request):
    # run_long_all.delay()
    Engine.run_long_all()
    return Response('ok')


@api_view()
def terminate_short_all_strategies(Request):
    # terminate_short_all.delay()
    Engine.terminate_short_all()
    return Response('ok')


@api_view()
def terminate_long_all_strategies(Request):
    # terminate_long_all.delay()
    Engine.terminate_long_all()
    return Response('ok')


@api_view()
def terminate_all_strategies(Request):
    terminate_all.delay()
    # Engine.terminate_all()
    return Response('ok')


@api_view()
def check_risk_all_strategies(Request):
    # check_risk_all.delay()
    Engine.check_risk_all()
    return Response('ok')


@api_view(['Put'])
def update_strategy_symbol(request):
    data = request.data
    symbols = StrategySymbol.objects.filter(
        strategy_execution_task_id=data['strategyExecutionTask'])
    for symbol in symbols:
        if symbol.position == 'short':
            symbol.symbol_id = data['strategyExecutionTaskSymbolShort']
        else:
            symbol.symbol_id = data['strategyExecutionTaskSymbolLong']
        symbol.save()

    return Response('ok')


# @api_view()
# def strategy_return():
