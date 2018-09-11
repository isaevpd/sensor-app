from unittest import mock

from django.test import TestCase

from sensor.constants import SENSOR_DATA_URI, WEATHER_DATA_URI, EXTERNAL_API_TIMEOUT
from sensor.tasks import (
    fetch_sensor_data,
    fetch_weather,
    update_statistics,
    update_helsinki_temperature
)


class MockResponse:
    """
    Class to mock requests.Response objects,
    feel free to adjust it to match the use case
    """
    def __init__(self, json_data):
        self.json_data = json_data

    def json(self):
        return self.json_data

    @property
    def ok(self):
        return True


class SensorTasksTest(TestCase):
    @mock.patch(
        'requests.get',
        return_value=MockResponse(
            json_data={
                "id": "iddqd",
                "data": 23.91569438663249,
                "timestamp": 1530127249766
            }
        )
    )
    @mock.patch('sensor.tasks.sensor_fetched.send')
    def test_fetch_sensor_data(self, signal_sent_mock, get_mock):
        """
        Http request to fetch sensor data is sent to the correct URI
        and sensor_fetched signal is fired
        """
        sensor_id = 'iddqd'
        fetch_sensor_data(sensor_id)
        get_mock.assert_called_once_with(
            SENSOR_DATA_URI.format(sensor_id=sensor_id),
            timeout=EXTERNAL_API_TIMEOUT
        )

        kwargs_to_send_signal_with = {
            'sender': fetch_sensor_data,
            'sensor_id': 'iddqd',
            'timestamp': 1530127249766,
            'value': 23.91569438663249
        }
        signal_sent_mock.assert_called_once_with(
            **kwargs_to_send_signal_with
        )

    @mock.patch(
        'requests.get',
        return_value=MockResponse(
            json_data={
                "temperature": 22.19
            }
        )
    )
    @mock.patch('sensor.tasks.weather_fetched.send')
    def test_fetch_weather_data(self, signal_sent_mock, get_mock):
        """
        Http request to fetch weather is sent to the correct URI
        and weather_fetched signal is fired
        """
        fetch_weather()
        get_mock.assert_called_once_with(
            WEATHER_DATA_URI,
            timeout=EXTERNAL_API_TIMEOUT
        )

        kwargs_to_send_signal_with = {
            'sender': fetch_weather,
            'temperature': 22.19,
        }
        signal_sent_mock.assert_called_once_with(
            **kwargs_to_send_signal_with
        )

    @mock.patch('sensor.models.SensorManager.update_sensor_statistics')
    def test_update_statistics_handler(self, mock_sensor_update):
        """
        update_statistics calls SensorManager.update_sensor_statistics
        """
        update_statistics(
            'some_sender',
            'iddqd',
            1530127249766,
            23.91569438663249
        )
        mock_sensor_update.assert_called_once_with(
            "iddqd",
            23.91569438663249,
        )

    @mock.patch('sensor.models.SensorManager.update_helsinki_temperature')
    def test_update_weather_handler(self, mock_helsinki_update):
        """
        update_helsinki_temperature calls SensorManager.update_helsinki_temperature
        """
        temp = 23.91569438663249
        update_helsinki_temperature('some_sender', temp)
        mock_helsinki_update.assert_called_once_with(
            temp
        )
