from django.urls import path
from sensor.views import sensor_statistics, temperature_difference


urlpatterns = [
    path(
        'diff/<str:sensor_id>/',
        temperature_difference,
        name='temperature_difference'
    ),
    path(
        '',
        sensor_statistics,
        name='sensor_statistics'
    ),
]
