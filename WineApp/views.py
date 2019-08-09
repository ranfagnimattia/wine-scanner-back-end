from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

import WineApp.algorithms.correlation as cor
import WineApp.algorithms.exponential_smoothing as es
import WineApp.algorithms.lstm as ls
import WineApp.algorithms.seasonal_decompose as sd
import WineApp.data.sensor_data as sensor_data
from WineApp.models import Sensor


def index(request):
    history = []
    # wine = Wine.objects.get(pk=2)
    # history = list(wine.weatherhistory_set.all()[:10])
    # history.append('...')
    # history += list(wine.weatherhistory_set.all().order_by('-pk')[:10])[::-1]
    # history = import_history()
    return render(request, 'WineApp/index.html', {'list': history})


def show_data(request):
    data, sensor, values, trend = sensor_data.get_daily_data()
    data_js = _daily_data_js(data, sensor, values, trend)
    data_js['ajax_url'] = reverse('WineApp:ajax.getDailyData')
    return render(request, 'WineApp/daily_data.html', {
        'sensors': Sensor.objects.all(),
        'data_js': data_js
    })


# Ajax
def get_daily_data(request):
    sensor_id = request.GET.get('sensor_id', 1)
    data, sensor, values, trend = sensor_data.get_daily_data(sensor_id)
    return JsonResponse(_daily_data_js(data, sensor, values, trend))


def _daily_data_js(data, sensor, values, trend):
    return {
        'data': data,
        'last': values[-1],
        'lastMonth': values[-31:],
        'trend': trend,
        'sensor': {'tot': sensor.tot, 'values': sensor.values, 'id': sensor.id, 'name': sensor.name,
                   'unit': sensor.unit}
    }


def update_daily_data(request):
    data = sensor_data.update_daily_data()
    return render(request, 'WineApp/index.html', {'list': data})


def update_realtime_data(request):
    data = sensor_data.update_realtime_data()
    return render(request, 'WineApp/index.html', {'list': data})


def expsmoothing(request, field, measure):
    pred, actual, dates = es.exponential_smoothing(field, measure)
    data = {'prediction': pred, 'actual': actual, 'dates': dates}
    return render(request, 'WineApp/predict.html', data)


def lstm(request, field, measure):
    pred, actual, dates = ls.lstm(field, measure)
    data = {'prediction': pred, 'actual': actual, 'dates': dates}
    return render(request, 'WineApp/predict.html', data)


def decompose(request, field):
    sd.stl(field)
    return render(request, 'WineApp/decompose.html')


def correlation(request):
    cor.correlation()
    return render(request, 'WineApp/correlation.html')
