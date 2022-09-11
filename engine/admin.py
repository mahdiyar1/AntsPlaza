from django.contrib import admin
from . import models


@admin.register(models.Trader)
class TraderAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ApiInformation)
class ApiInformationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.StrategyClass)
class StrategyClassAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_strategy_execution_id']


@admin.register(models.StrategySetting)
class StrategySettingAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['is_fund_provide_order']


@admin.register(models.Symbol)
class SymbolAdmin(admin.ModelAdmin):
    pass


@admin.register(models.StrategySymbol)
class StrategySymbolAdmin(admin.ModelAdmin):
    list_display = ['id', 'symbol_id', 'position',
                    'strategy_id', 'strategy_execution_task_id']


@admin.register(models.Borrow)
class LoanAdmin(admin.ModelAdmin):
    pass


@admin.register(models.StrategyExecution)
class ExecutionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ManualSymbol)
class ManualSymbolAdmin(admin.ModelAdmin):
    pass
