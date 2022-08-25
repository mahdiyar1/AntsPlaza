import threading
from celery.signals import celeryd_after_setup
from celery import shared_task
from .kucoin_websocket_feed import market_data_feed
from .algo_engine import Engine
from django_celery_beat.models import PeriodicTask


@shared_task
def run_short(strategy_id: int):
    Engine.run_short(strategy_id)


@shared_task
def run_long(strategy_id: int):
    Engine.run_long(strategy_id)


@shared_task
def terminate_short(strategy_id: int):
    Engine.terminate_short(strategy_id)


@shared_task
def terminate_long(strategy_id: int):
    Engine.terminate_long(strategy_id)


@shared_task
def check_risk(strategy_id):
    Engine.check_risk(strategy_id)


@shared_task
def terminate(strategy_id):
    Engine.terminate(strategy_id)


@shared_task
def run_short_all(strategy_execution_task_name):
    strategy_execution_task_id =  PeriodicTask.objects.filter(name=strategy_execution_task_name).first().id
    Engine.run_short_all(strategy_execution_task_id)


@shared_task
def run_long_all():
    Engine.run_long_all()


@shared_task
def terminate_short_all():
    Engine.terminate_short_all()


@shared_task
def terminate_long_all():
    Engine.terminate_long_all()


@shared_task
def terminate_all():
    Engine.terminate_all()


@shared_task
def check_risk_all():
    Engine.check_risk_all()


@celeryd_after_setup.connect
def init(**kwargs):
    Engine.init()
    market_data_feeds = threading.Thread(
        target=market_data_feed, daemon=True)
    market_data_feeds.start()


@shared_task
def test(strategy_execution_task_id):
    print(strategy_execution_task_id)
