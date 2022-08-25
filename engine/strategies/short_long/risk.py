from .helper import Helper
from ...models import StrategyExecution, StrategySetting, Symbol


class Risk():

    def __init__(self, strategy):
        super().__init__()
        self.strategy = strategy
        self.helper: Helper = strategy.helper

    def short(self):
        sell_order = self.helper.get_short_sell_order()
        interest = self.helper.get_borrow_order().interest

        buy_amount = sell_order.amount + interest
        current_price = Symbol.objects.get(
            pk=sell_order.symbol.id).kline_open_1_min

        adjusted_data = self.calculate_fee_included_buy_price(
            sell_order.symbol, current_price, buy_amount)

        adjusted_current_price = adjusted_data[0]
        sell_price = sell_order.average_price_fee_included

        return_ratio = (sell_price - adjusted_current_price) / sell_price

        return_ratio = return_ratio * self.strategy.leverage

        if return_ratio >= 0:
            profit_ratio = StrategySetting.objects.filter(
                strategy_id=self.strategy.strategy_id, name='short_take_profit_ratio').first().value
            if return_ratio > profit_ratio:
                self.strategy.terminate_short()
                execution = StrategyExecution.objects.get(
                    pk=self.strategy.execution_id)
                execution.last_short_return_ratio = return_ratio
                execution.save()

            short_return = sell_order.cost_fee_adjusted - adjusted_data[1]
            return [return_ratio, short_return]

        loss_ratio = StrategySetting.objects.filter(
            strategy_id=self.strategy.strategy_id, name='short_stop_loss_ratio').first().value
        if -return_ratio > loss_ratio:
            self.strategy.terminate_short()
            # TODO close short position result
            execution = StrategyExecution.objects.get(
                pk=self.strategy.execution_id)
            execution.last_short_return_ratio = return_ratio
            execution.save()

        short_return = sell_order.cost_fee_adjusted - adjusted_data[1]

        return [return_ratio, short_return]

    def long(self):
        buy_order = self.helper.get_long_buy_order()
        buy_price = buy_order.average_price_fee_included
        current_price = Symbol.objects.get(
            pk=buy_order.symbol.id).kline_open_1_min
        adjusted_data = self.calculate_fee_included_sell_price(
            buy_order.symbol, current_price, buy_order.amount)
        adjusted_current_price = adjusted_data[0]
        return_ratio = (adjusted_current_price - buy_price) / buy_price

        return_ratio = return_ratio * self.strategy.leverage

        if return_ratio >= 0:
            profit_ratio = StrategySetting.objects.filter(
                strategy_id=self.strategy.strategy_id, name='long_take_profit_ratio').first().value
            if return_ratio > profit_ratio:
                self.strategy.terminate_long()
                execution = StrategyExecution.objects.get(
                    pk=self.strategy.execution_id)
                execution.last_long_return_ratio = return_ratio
                execution.save()
            
            long_return = adjusted_data[1] - buy_order.cost_fee_adjusted

            return [return_ratio, long_return]

        loss_ratio = StrategySetting.objects.filter(
            strategy_id=self.strategy.strategy_id, name='long_stop_loss_ratio').first().value
        if -return_ratio > loss_ratio:
            self.strategy.terminate_long()
            execution = StrategyExecution.objects.get(
                pk=self.strategy.execution_id)
            execution.last_long_return_ratio = return_ratio
            execution.save()

        long_return = adjusted_data[1] - buy_order.cost_fee_adjusted

        return [return_ratio, long_return]

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
        return [adjusted_price, adjusted_cost]

    def calculate_fee_included_sell_price(self, symbol, current_price, amount):
        cost = current_price * amount
        adjusted_cost = cost - cost * symbol.maker_fee_rate
        adjusted_price = adjusted_cost / amount
        return [adjusted_price, adjusted_cost]
