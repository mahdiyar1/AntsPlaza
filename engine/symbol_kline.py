from decimal import Decimal
from pprint import pprint


class SymbolKline():
    symbols_kline_open_1min = {}

    @classmethod
    async def update_kline(cls, symbol, price):
        cls.symbols_kline_open_1min[symbol] = Decimal(price)
        # pprint(cls.symbols_kline_open_1min)
        # pprint(cls.symbols_kline_open_1min)
        
