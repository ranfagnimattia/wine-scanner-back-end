from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

import WineApp.algorithms.correlation as cor
import WineApp.algorithms.exponential_smoothing as es
import WineApp.algorithms.lstm as ls
import WineApp.algorithms.seasonal_decompose as sd
import WineApp.data.sensor_data as sensor_data
import WineApp.data.update_data as update_data
from WineApp.data import prediction
from WineApp.models import Sensor


def index(request):
    history = []
    return render(request, 'WineApp/index.html', {'list': history})


# Daily Dashboard
def show_daily_data(request):
    data_js = sensor_data.get_daily_data()
    data_js.update({
        'getUrl': reverse('WineApp:ajax.getDailyData'),
        'updateUrl': reverse('WineApp:ajax.updateDailyData')
    })
    return render(request, 'WineApp/daily_data.html', {
        'sensors': Sensor.objects.all(),
        'data_js': data_js
    })


def ajax_get_daily_data(request):
    sensor_id = request.GET.get('sensorId', 1)
    return JsonResponse(sensor_data.get_daily_data(sensor_id))


def ajax_update_daily_data(request):
    return JsonResponse(update_data.update_daily_data())


# RealTime Dashboard
def show_realtime_data(request):
    data_js = sensor_data.get_realtime_data()
    data_js.update({
        'autoUpdate': True,
        'getUrl': reverse('WineApp:ajax.getRealTimeData'),
        'updateUrl': reverse('WineApp:ajax.updateRealTimeData')
    })
    sensors = Sensor.objects.all()
    for sensor in sensors:
        sensor.disabled = not sensor.values
    return render(request, 'WineApp/realtime_data.html', {
        'sensors': sensors,
        'data_js': data_js
    })


def ajax_get_realtime_data(request):
    sensor_id = request.GET.get('sensorId', 1)
    return JsonResponse(sensor_data.get_realtime_data(sensor_id))


def ajax_update_realtime_data(request):
    return JsonResponse(update_data.update_realtime_data())


# Anomalies Dashboard
def show_anomalies(request):
    data_js = sensor_data.get_prediction_data()
    data_js.update({
        'getUrl': reverse('WineApp:ajax.getAnomalies'),
        'updateUrl': reverse('WineApp:ajax.updateAnomalies')
    })
    sensors = Sensor.objects.all()
    for sensor in sensors:
        sensor.disabled = sensor.startTestSet is None
    return render(request, 'WineApp/anomalies.html', {
        'sensors': sensors,
        'multilevel': True,
        'data_js': data_js
    })


def ajax_get_anomalies(request):
    sensor_id = request.GET.get('sensorId', 1)
    measure = request.GET.get('measure')
    return JsonResponse(sensor_data.get_prediction_data(sensor_id, measure))


def ajax_update_anomalies(request):
    return JsonResponse(prediction.update_prediction())


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
