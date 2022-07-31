import imp
from celery import shared_task
from .algo_engine import Engine


@shared_task
def run(strategy_id: int):
    Engine.run(strategy_id)


@shared_task
def check_risk(strategy_id):
    Engine.check_risk(strategy_id)
