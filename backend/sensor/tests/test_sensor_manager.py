from unittest import mock

from django.test import TestCase
from sensor.models import SensorManager


class SensorManagerTest(TestCase):
    @mock.patch('sensor.models.cache')
    def test_update_statistics_empty(self, mock_cache):
        """
        SensorManager.update_sensor_statistics
        puts data in django cache with timeout=None
        so it doesn't expire
        """
        mock_cache.get.return_value = {}
        SensorManager.update_sensor_statistics(
            'iddqd',
            23.91569438663249
        )
        mock_cache.set.assert_called_once_with(
            "iddqd",
            {
                "count": 1,
                "avg": 23.91569438663249,
                "temperature": 23.91569438663249,
                "total": 23.91569438663249
            },
            timeout=None
        )

    @mock.patch('sensor.models.cache')
    def test_update_statistics_non_empty(self, mock_cache):
        """
        SensorManager.update_sensor_statistics correctly
        updates count/avg in django cache
        """
        previous_temp = 24.91569438663249
        previous_total = previous_temp
        previous_avg = previous_temp
        mock_cache.get.return_value = {
            "count": 1,
            "avg": previous_avg,
            "temperature": previous_temp,
            "total": previous_total
        }
        new_temp = 23.91569438663249
        SensorManager.update_sensor_statistics(
            'iddqd',
            new_temp
        )

        new_total = new_temp + previous_temp
        mock_cache.set.assert_called_once_with(
            "iddqd",
            {
                "count": 2,
                "avg": new_total / 2,
                "temperature": new_temp,
                "total": new_total
            },
            timeout=None
        )

    @mock.patch('sensor.models.cache.set')
    def test_update_helsinki_temperature(self, mock_cache_set):
        """
        SensorManager.update_helsinki_temperature saves temperature
        to django cache with "helsinki_temperature" key and no
        expiration time
        """
        temp = 23.91569438663249
        SensorManager.update_helsinki_temperature(temp)
        mock_cache_set.assert_called_once_with(
            'helsinki_temperature', temp, timeout=None
        )

    @mock.patch('sensor.models.cache')
    def test_get_statistics(self, mock_cache):
        """
        SensorManager.get_statistics() returns data
        for all sensors specified in constants.SUPPORTED_SENSORS
        from django cache
        """
        mock_cache.get_many.return_value = {
            "abba5": {"count": 36, "avg": 23.76197165651435},
            "abba": {"count": 12500000, "avg": 25.725636626332992},
            "acdc": {"count": 12500000, "avg": 25.186297131260652},
            "iddqd": {"count": 12500036, "avg": 25.87519048725104},
            "idkfa": {"count": 12500000, "avg": 27.081039930247535}
        }
        stats = SensorManager.get_statistics()
        self.assertCountEqual(
            stats,
            [
                {'id': 'abba5', 'count': 36, 'avgTemp': 23.76197165651435},
                {'id': 'abba', 'count': 12500000, 'avgTemp': 25.725636626332992},
                {'id': 'acdc', 'count': 12500000, 'avgTemp': 25.186297131260652},
                {'id': 'iddqd', 'count': 12500036, 'avgTemp': 25.87519048725104},
                {'id': 'idkfa', 'count': 12500000, 'avgTemp': 27.081039930247535}
            ]
        )

    @mock.patch('sensor.models.SensorManager.get')
    def test_get_helsinki_temp_diff(self, mock_sensor_manager_get):
        """
        SensorManager.get_helsinki_temp_diff gets value for
        a given sensor and helsinki_temperature from django cache
        and returns abs(sensor_temp - helsinki_temperature)
        """
        temp = 23.7619716565143
        helsinki_temp = 19.08
        mock_sensor_manager_get.side_effect = [
            {'temperature': temp},
            helsinki_temp
        ]
        diff = SensorManager.get_helsinki_temp_diff('iddqd')
        self.assertEqual(diff, temp - helsinki_temp)

    @mock.patch('sensor.models.SensorManager.get')
    def test_get_helsinki_temp_diff_no_data(self, mock_sensor_manager_get):
        """
        SensorManager.get_helsinki_temp_diff returns None
        if no data for sensor is present
        """
        helsinki_temp = 19.08
        mock_sensor_manager_get.side_effect = [
            {},
            helsinki_temp
        ]
        diff = SensorManager.get_helsinki_temp_diff('foo')
        self.assertIsNone(diff)
