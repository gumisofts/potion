from celery.schedules import crontab

from tasks_handler.celery import app

app.conf.beat_schedule = {}
