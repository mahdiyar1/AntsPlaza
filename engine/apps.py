from django.apps import AppConfig


class EngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'engine'

    def ready(self):
        import threading
        from .kucoin_websocket_feed import market_data_feed
        from .algo_engine import Engine
        Engine.init()
        market_data_feeds = threading.Thread(
            target=market_data_feed, daemon=True)
        market_data_feeds.start()
        pass
