from decimal import Decimal
from asgiref.sync import sync_to_async

from .models import Symbol


class SymbolKline():
    symbols_kline_open_1min = {}
    counter = 0

    @classmethod
    async def update_kline(cls, symbol, price):
        cls.symbols_kline_open_1min[symbol] = Decimal(price)
        cls.counter = cls.counter + 1
        if cls.counter % 10 == 0:
            await sync_to_async(cls.persist)()

    @classmethod
    def persist(cls):
        for symbol in cls.symbols_kline_open_1min.keys():
            symbol_in_db = Symbol.objects.get(pk=symbol)
            symbol_in_db.kline_open_1_min = cls.symbols_kline_open_1min[symbol]
            symbol_in_db.save()
