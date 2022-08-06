from .helper import Helper
from ...symbol_kline import SymbolKline
from ...models import StrategyExecution, StrategySetting


class Risk():

    def __init__(self, strategy):
        super().__init__()
        self.strategy = strategy
        self.helper: Helper = strategy.helper

    def short(self):
        sell_order = self.helper.get_short_sell_order()
        interest = self.helper.get_borrow_order().interest

        buy_amount = sell_order.amount + interest
        current_price = SymbolKline.symbols_kline_open_1min[sell_order.symbol.id]

        adjusted_current_price = self.calculate_fee_included_buy_price(sell_order.symbol, current_price, buy_amount)
        sell_price = sell_order.average_price_fee_included

        ratio = (sell_price - adjusted_current_price) / sell_price

        ratio = ratio * self.strategy.leverage

        if ratio >= 0:
            profit_ratio = StrategySetting.objects.filter(
                strategy_id=self.strategy.strategy_id, name='short_take_profit_ratio').first().value
            if ratio > profit_ratio:                
                self.strategy.short.cancel()
                # TODO close short position result
                execution = StrategyExecution.objects.get(pk=self.strategy.execution_id)
                execution.last_short_return = ratio
                execution.save()
            return ratio

        loss_ratio = StrategySetting.objects.filter(
            strategy_id=self.strategy.strategy_id, name='short_stop_loss_ratio').first().value
        if -ratio > loss_ratio:
            self.strategy.short.cancel()
                # TODO close short position result
            execution = StrategyExecution.objects.get(pk=self.strategy.execution_id)
            execution.last_short_return = ratio
            execution.save()
        return ratio

    def long(self):
        buy_order = self.helper.get_long_buy_order()
        buy_price = buy_order.average_price_fee_included
        current_price = SymbolKline.symbols_kline_open_1min[buy_order.symbol.id]
        adjusted_current_price = self.calculate_fee_included_sell_price(buy_order.symbol, current_price, buy_order.amount)
        ratio = (adjusted_current_price - buy_price) / buy_price

        ratio = ratio * self.strategy.leverage

        if ratio >= 0:
            profit_ratio = StrategySetting.objects.filter(
                strategy_id=self.strategy.strategy_id, name='long_take_profit_ratio').first().value
            if ratio > profit_ratio:
                self.strategy.long.cancel()
                #TODO return result
                execution = StrategyExecution.objects.get(pk=self.strategy.execution_id)
                execution.last_long_return = ratio
                execution.save()
            return ratio

        loss_ratio = StrategySetting.objects.filter(
            strategy_id=self.strategy.strategy_id, name='long_stop_loss_ratio').first().value
        if -ratio > loss_ratio:
            self.strategy.long.cancel()
            #TODO return result
            execution = StrategyExecution.objects.get(pk=self.strategy.execution_id)
            execution.last_long_return = ratio
            execution.save()
        return ratio

    def portfolio(self, short_ratio, long_ratio):
        portfolio_ratio = short_ratio + long_ratio

        if portfolio_ratio >= 0:
            profit_ratio = StrategySetting.objects.filter(
                strategy_id=self.strategy.strategy_id, name='portfolio_take_profit_ratio').first().value
            if portfolio_ratio > profit_ratio:
                self.strategy.terminate()
                return

        loss_ratio = StrategySetting.objects.filter(
            strategy_id=self.strategy.strategy_id, name='portfolio_stop_loss_ratio').first().value

        if -portfolio_ratio > loss_ratio:
            self.strategy.terminate()

    def calculate_fee_included_buy_price(self, symbol, current_price, amount):
        cost = current_price * amount
        adjusted_cost = cost + cost * symbol.maker_fee_rate
        adjusted_price = adjusted_cost / amount
        return adjusted_price

    def calculate_fee_included_sell_price(self, symbol, current_price, amount):
        cost = current_price * amount
        adjusted_cost = cost - cost * symbol.maker_fee_rate
        adjusted_price = adjusted_cost / amount
        return adjusted_price
