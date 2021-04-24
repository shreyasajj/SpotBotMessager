from celery import Celery
import config


def make_celery():
    celery2 = Celery(__name__, broker=config.CELERY_BROKER)
    celery2.conf.update(config.as_dict())
    return celery2


celery = make_celery()
