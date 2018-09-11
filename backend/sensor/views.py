from django.http import JsonResponse, Http404

from sensor.models import SensorManager
from rest_framework.decorators import api_view


@api_view()
def sensor_statistics(request):
    stats = SensorManager.get_statistics()
    return JsonResponse({'sensors': stats})


@api_view()
def temperature_difference(request, sensor_id):
    temp = SensorManager.get_helsinki_temp_diff(sensor_id)
    if temp:
        payload = {
            "differenceInCelsius": temp
        }
        return JsonResponse(payload)
    else:
        raise Http404('No such sensor')
