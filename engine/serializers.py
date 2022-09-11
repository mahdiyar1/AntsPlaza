from dataclasses import fields
from rest_framework import serializers
from django_celery_beat.models import PeriodicTask
from .models import ApiInformation, ManualSymbol, Order, Strategy, StrategyExecution, StrategySetting, StrategySymbol, Symbol


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'trader', 'strategy', 'symbol', 'status', 'side', 'position',
                  'average', 'averagePriceFeeIncluded', 'amount', 'cost', 'costFeeAdjusted', 'fee', 'datetime']

    averagePriceFeeIncluded = serializers.DecimalField(
        max_digits=24, decimal_places=12, source='average_price_fee_included')
    costFeeAdjusted = serializers.DecimalField(
        max_digits=24, decimal_places=12, source="cost_fee_adjusted")


class StrategySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategySetting
        fields = ['id', 'name', 'value', 'comment', 'strategy']


class ManuelSymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualSymbol
        fields = ['id', 'kucoin_symbol_choice', 'binance_symbol_choice']


class ApiInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiInformation
        fields = ['id', 'key', 'secret', 'password', 'trader', 'exchange']


class StrategySymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategySymbol
        fields = ['id', 'symbol', 'position', 'strategy',
                  'strategy', 'strategyExecutionTaskId']

    strategyExecutionTaskId = serializers.IntegerField(
        source='strategy_execution_task_id')


class SymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symbol
        fields = ['id']


class PeriodicTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = ['id', 'name', 'task']


class StrategyExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategyExecution
        fields = ['last_short_return_ratio', 'last_long_return_ratio',
                  'last_short_return', 'last_long_return', 'is_strategy_end', 'short_symbol', 'long_symbol',
                  'is_short_success', 'is_long_success', 'is_short_closed', 'is_long_closed']


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ['id', 'last_strategy_execution']

    last_strategy_execution = StrategyExecutionSerializer()
