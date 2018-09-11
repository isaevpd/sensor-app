import logging

import requests
from celery import task
from celery.signals import celeryd_init
from celery.utils.dispatch import Signal
from .models import SensorManager

from .constants import SENSOR_DATA_URI, WEATHER_DATA_URI, EXTERNAL_API_TIMEOUT

sensor_fetched = Signal(providing_args=['sensor_id', 'timestamp', 'value'])
weather_fetched = Signal(providing_args=['temperature'])


def write_sensor_event(sender, sensor_id: str, timestamp: int, value: float, *args, **kwargs):
    SensorManager.write_sensor_event(
        sensor_id,
        timestamp,
        value
    )


def update_statistics(sender, sensor_id: str, timestamp, value: float, *args, **kwargs):
    SensorManager.update_sensor_statistics(sensor_id, value)


def update_helsinki_temperature(sender, temperature: float, *args, **kwargs):
    SensorManager.update_helsinki_temperature(temperature)


@celeryd_init.connect
def init_signals(*args, **kwargs):
    sensor_fetched.connect(
        write_sensor_event,
        dispatch_uid='write-sensor-to-db'
    )
    sensor_fetched.connect(
        update_statistics,
        dispatch_uid='update-cache-statistics'
    )
    weather_fetched.connect(
        update_helsinki_temperature,
        dispatch_uid='update-cache-weather'
    )


@task(bind=True)
def fetch_sensor_data(self, sensor_id: str):
    response = requests.get(
        SENSOR_DATA_URI.format(sensor_id=sensor_id),
        timeout=EXTERNAL_API_TIMEOUT
    )
    if response.ok:
        data = response.json()
        kwargs = {
            'sender': self,
            'sensor_id': data['id'],
            'timestamp': data['timestamp'],
            'value': data['data']
        }
        sensor_fetched.send(**kwargs)
    else:
        logging.error(
            'Couldn"t fetch sensor data',
            extra={'status_code': response.status_code}
        )


@task(bind=True)
def fetch_weather(self):
    response = requests.get(
        WEATHER_DATA_URI,
        timeout=EXTERNAL_API_TIMEOUT
    )
    if response.ok:
        data = response.json()
        weather_fetched.send(sender=self, temperature=data['temperature'])
    else:
        logging.error(
            'Couldn"t fetch weather data',
            extra={
                'status_code': response.status_code,
                'timeout': EXTERNAL_API_TIMEOUT
            }
        )
