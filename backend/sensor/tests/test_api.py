from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase


class SensorApiTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='testuser', password='12345'
        )
        self.token = self.client.post(
            '/api/token',
            data={
                'username': 'testuser',
                'password': '12345'
            }
        ).json()['access']

    @mock.patch('sensor.views.SensorManager.get_statistics')
    def test_sensor_statistics(self, mocked_get_statistics):
        """
        /sensor/ endpoint returns results from SensorManager.get_statistics
        """
        data = [
            {'id': 'abba5', 'count': 36, 'avgTemp': 23.76197165651435},
            {'id': 'abba', 'count': 12500000, 'avgTemp': 25.725636626332992},
            {'id': 'acdc', 'count': 12500000, 'avgTemp': 25.186297131260652},
            {'id': 'iddqd', 'count': 12500036, 'avgTemp': 25.87519048725104},
            {'id': 'idkfa', 'count': 12500000, 'avgTemp': 27.081039930247535}
        ]
        mocked_get_statistics.return_value = data
        response = self.client.get(
            '/sensor/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        mocked_get_statistics.assert_called_once()
        self.assertDictEqual(
            response.json(),
            {
                'sensors': data
            }
        )

    @mock.patch('sensor.views.SensorManager.get_helsinki_temp_diff')
    def test_temperature_difference(self, mocked_get_helsinki_temp_diff):
        """
        /diff/<sensor_id> returns results from SensorManager.get_helsinki_temp_diff
        """
        mocked_get_helsinki_temp_diff.return_value = 23.7619716565143
        response = self.client.get(
            '/sensor/diff/iddqd/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        mocked_get_helsinki_temp_diff.assert_called_once()
        self.assertDictEqual(
            response.json(),
            {
                'differenceInCelsius': 23.7619716565143
            }
        )

    @mock.patch('sensor.models.SensorManager.get_helsinki_temp_diff')
    def test_temperature_difference_not_found(self, mocked_get_helsinki_temp_diff):
        """
        /diff/<sensor_id> returns 404 if no such sensor exists
        """
        mocked_get_helsinki_temp_diff.return_value = None
        response = self.client.get(
            '/sensor/diff/iddqd/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        mocked_get_helsinki_temp_diff.assert_called_once()
        self.assertEqual(response.status_code, 404)
