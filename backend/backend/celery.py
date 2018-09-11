from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery(
    'backend',
    broker='redis://localhost:6379/0'
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'fetch-sensor-data-iddqd': {
        'task': 'sensor.tasks.fetch_sensor_data',
        'schedule': 1.0,
        'args': ('iddqd',)
    },
    'fetch-sensor-data-abba5': {
        'task': 'sensor.tasks.fetch_sensor_data',
        'schedule': 1.0,
        'args': ('abba5',)
    },
    'fetch_and_cache_weather': {
        'task': 'sensor.tasks.fetch_weather',
        'schedule': 5.0
    }
}
