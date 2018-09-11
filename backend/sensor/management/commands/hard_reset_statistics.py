from django.core.management.base import BaseCommand
from sensor.models import SensorManager


class Command(BaseCommand):
    """
    "Hard reset of statistics" for all sensors
    useful when you need to initialize the data or debug the code

    TODO: add service to send an alert if data doesn't match
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--health_check',
            action='store_true',
            dest='health_check',
            help='Run health check instead of updating cache',
        )

    def update_cache(self, stats, health_check=False):
        """
        Calls SensorManager API to update the statistics
        or asserts that values are the same if health_check is set
        to True
        """
        print(stats)
        for sensor_id, temp, count, avg, total in stats:
            if health_check:
                current_sensor = SensorManager.get(sensor_id)
                assert current_sensor is not None
                assert current_sensor['avg'] == avg
                assert current_sensor['count'] == count
                assert current_sensor['temperature'] == temp
                assert current_sensor['total'] == total
                print(f'Data for {sensor_id} is up to date')
            else:
                SensorManager.set(
                    sensor_id,
                    count,
                    avg,
                    temp,
                    total
                )

    def handle(self, *args, **options):
        health_check = options.get('health_check')
        stats = SensorManager.get_stats_for_all_sensors()
        self.update_cache(stats, health_check=health_check)
