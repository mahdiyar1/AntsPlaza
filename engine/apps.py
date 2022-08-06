from django.apps import AppConfig


class EngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'engine'

    def ready(self):
        import time
        import threading
        from .kucoin_websocket_feed import market_data_feed
        from .algo_engine import Engine
        market_data_feed = threading.Thread(target=market_data_feed, daemon=True)
        market_data_feed.start()
        Engine.init()
        # time.sleep(5)
        # Engine.run(1)        
        # while True:
        #     Engine.check_risk(1)
        #     # Engine.terminate(1)
        #     time.sleep(2)
