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
    data, sensor = sensor_data.get_daily_data()

    return render(request, 'WineApp/daily_data.html', {
        'sensors': Sensor.objects.all(),
        'data_js': {
            'data': data,
            'ajax_url': reverse('WineApp:ajax.getDailyData'),
            'sensor': {'tot': sensor.tot, 'val': sensor.values, 'id': sensor.id, 'name': sensor.name,
                       'unit': sensor.unit}
        }})


# Ajax
def get_daily_data(request):
    sensor_id = request.GET.get('sensor_id', 1)
    data, sensor = sensor_data.get_daily_data(sensor_id)
    return JsonResponse({
        'data': data,
        'sensor': {'tot': sensor.tot, 'val': sensor.values, 'id': sensor.id, 'name': sensor.name,
                   'unit': sensor.unit}
    })


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


def dashboard(request):
    return render(request, 'WineApp/dashboard.html')
