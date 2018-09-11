from django.core.cache import cache
from django.db import connection

from sensor.constants import SUPPORTED_SENSORS


class SensorManager:
    """
    This is a namespace for sensor-related methods
    Normally, it would be a django model it would impose
    some restrictions and reduce performance when using an ORM
    so we stick to raw SQL here

    NB: cache manipulations should happen here not in views or tasks
    """
    HELSINKI_TEMPERATURE_KEY = 'helsinki_temperature'

    @staticmethod
    def write_sensor_event(sensor_id: str, timestamp: int, value: float):
        # django connection.cursor raises a TypeError when doing the same thing
        # as arguments are interpolated differently:
        # https://github.com/django/django/blob/c1c163b42717ed5e051098ebf0e2f5c77810f20e/django/db/backends/sqlite3
        # /operations.py#L147
        # fetching original cursor object works just fine:
        conn = connection.cursor().db.connection
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO datas VALUES (?, ?, ?)',
            (sensor_id, timestamp, value)
        )
        conn.commit()

    @classmethod
    def update_sensor_statistics(cls, sensor_id: str, value: float):
        sensor_data = cls.get(sensor_id, {})
        old_count = sensor_data.get('count', 0)
        count = old_count + 1
        old_total = sensor_data.get('total', 0)
        total = old_total + value
        avg = total / count
        return cls.set(
            sensor_id,
            count,
            avg,
            value,
            total
        )

    @classmethod
    def update_helsinki_temperature(cls, temperature: float):
        return cache.set(
            cls.HELSINKI_TEMPERATURE_KEY,
            temperature,
            timeout=None
        )

    @staticmethod
    def get_stats_for_all_sensors():
        """
        Calculate count, avg and latest temperature
        """
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, value, count(*), avg(value), sum(value)
            FROM datas
            GROUP BY id
            ORDER BY time DESC
            """
        )
        result = list(cursor)
        connection.close()
        return result

    @staticmethod
    def get(sensor_id, default=None):
        return cache.get(sensor_id, default)

    @staticmethod
    def set(sensor_id: str, count: int, avg, temperature: float, total: float):
        return cache.set(
            sensor_id,
            {
                'count': count,
                'avg': avg,
                'temperature': temperature,
                'total': total
            },
            timeout=None
        )

    @staticmethod
    def get_statistics():
        data = cache.get_many(SUPPORTED_SENSORS)
        sensors = []
        for sensor_id, details in data.items():
            sensors.append(
                {
                    'id': sensor_id,
                    'count': details['count'],
                    'avgTemp': details['avg']
                }
            )
        return sensors

    @classmethod
    def get_helsinki_temp_diff(cls, sensor_id: str):
        sensor_temp = cls.get(sensor_id, {}).get('temperature')
        helsinki_temp = cls.get(cls.HELSINKI_TEMPERATURE_KEY)
        try:
            return abs(sensor_temp - helsinki_temp)
        except TypeError:
            return None
