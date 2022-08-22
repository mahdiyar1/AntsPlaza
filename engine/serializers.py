from dataclasses import fields
from rest_framework import serializers
from django_celery_beat.models import PeriodicTask
from .models import Order, StrategySetting, StrategySymbol, Symbol


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'trader', 'strategy', 'symbol', 'status', 'side', 'position',
                  'average', 'averagePriceFeeIncluded', 'amount', 'cost', 'costFeeAdjusted', 'fee']

    averagePriceFeeIncluded = serializers.DecimalField(
        max_digits=24, decimal_places=12, source="average_price_fee_included")
    costFeeAdjusted = serializers.DecimalField(
        max_digits=24, decimal_places=12, source="cost_fee_adjusted")


class StrategySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategySetting
        fields = ['id', 'name', 'value', 'comment', 'strategy']


class StrategySymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategySymbol
        fields = ['id', 'symbol', 'position', 'strategy']


class SymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symbol
        fields = ['id']


class PeriodicTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = ['id', 'name']
