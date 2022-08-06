import asyncio
from pprint import pprint
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient
from .symbol_kline import SymbolKline


async def web_socket():
    async def update_kline(msg):
        data = msg['data']
        await SymbolKline.update_kline(data['symbol'],data['candles'][1])

    client = WsToken()
    ws_client = await KucoinWsClient.create(None, client, update_kline, private=False)
    await ws_client.subscribe('/market/candles:BTC-USDT_1min,BNB-USDT_1min') #TODO all symbols and connection check 
    while True:
        await asyncio.sleep(60)


def market_data_feed():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(web_socket())
    loop.close()
