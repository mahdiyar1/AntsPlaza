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
    pass


@admin.register(models.StrategySetting)
class StrategySettingAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Trade)
class TradeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MarginBalance)
class BalanceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Symbol)
class SymbolAdmin(admin.ModelAdmin):
    pass


@admin.register(models.StrategySymbol)
class StrategySymbolAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Borrow)
class LoanAdmin(admin.ModelAdmin):
    pass


@admin.register(models.StrategyExecution)
class ExecutionAdmin(admin.ModelAdmin):
    pass
