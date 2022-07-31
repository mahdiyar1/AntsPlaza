from django.apps import AppConfig


class EngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'engine'
    def ready(self):
        from .algo_engine import Engine
        Engine.init()
        Engine.run(1)
        
