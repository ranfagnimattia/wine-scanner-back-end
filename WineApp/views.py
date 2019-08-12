import time

from django.http import JsonResponse
from django.shortcuts import render

import WineApp.algorithms.correlation as cor
import WineApp.algorithms.exponential_smoothing as es
import WineApp.algorithms.lstm as ls
import WineApp.algorithms.seasonal_decompose as sd
import WineApp.data.sensor_data as sensor_data
import WineApp.data.update_data as update_data
from WineApp.models import Sensor


def index(request):
    history = []
    return render(request, 'WineApp/index.html', {'list': history})


def show_daily_data(request):
    data_js = sensor_data.get_daily_data()
    return render(request, 'WineApp/daily_data.html', {
        'sensors': Sensor.objects.all(),
        # 'multilevel': True,
        'data_js': data_js
    })


def show_real_time_data(request):
    update_data.update_realtime_data()
    sensor_data.get_real_time_data()
    return render(request, 'WineApp/real_time_data.html')


# Ajax
def ajax_get_daily_data(request):
    sensor_id = request.GET.get('sensor_id', 1)
    return JsonResponse(sensor_data.get_daily_data(sensor_id))


def ajax_update_daily_data(request):
    # time.sleep(3)
    return JsonResponse(update_data.update_daily_data())


# Update Data
def update_daily_data(request):
    start = time.time()
    data = update_data.update_daily_data()
    end = time.time()
    data.append('Time: ' + str(end - start))
    print(end - start)
    return render(request, 'WineApp/index.html', {'list': data})


def update_realtime_data(request):
    data = update_data.update_realtime_data()
    return render(request, 'WineApp/index.html', {'list': data})


# Algorithms
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
