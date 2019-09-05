from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

import WineApp.data.anomalies as anomalies_data
import WineApp.data.anomalies.get
import WineApp.data.anomalies.update
import WineApp.data.daily as daily_data
import WineApp.data.daily.get
import WineApp.data.daily.update
import WineApp.data.hourly as hourly_data
import WineApp.data.hourly.get
import WineApp.data.hourly.update
import WineApp.data.index as index
import WineApp.data.index.get
from WineApp.models import Sensor


# Index Dashboard
def show_index(request):
    data_js = index.get.get_data()
    data_js.update({
        'getUrl': reverse('WineApp:ajax.getIndex'),
        'updateUrl': reverse('WineApp:ajax.updateIndex')
    })
    sensors = Sensor.objects.all()
    for sensor in sensors:
        sensor.disabled = sensor.startTestSet is None
    return render(request, 'WineApp/index.html', {
        'sensors': sensors,
        'allSensors': True,
        'data_js': data_js
    })


def ajax_get_index(request):
    sensor_id = request.GET.get('sensorId', 0)
    return JsonResponse(index.get.get_data(sensor_id))


def ajax_update_index(request):
    return JsonResponse(anomalies_data.update.update_data())


# Daily Dashboard
def show_daily_data(request):
    data_js = daily_data.get.get_data()
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
    return JsonResponse(daily_data.get.get_data(sensor_id))


def ajax_update_daily_data(request):
    return JsonResponse(daily_data.update.update_data())


# Hourly Dashboard
def show_hourly_data(request):
    data_js = hourly_data.get.get_data()
    data_js.update({
        'autoUpdate': True,
        'getUrl': reverse('WineApp:ajax.getHourlyData'),
        'updateUrl': reverse('WineApp:ajax.updateHourlyData')
    })
    sensors = Sensor.objects.all()
    for sensor in sensors:
        sensor.disabled = not sensor.values
    return render(request, 'WineApp/hourly_data.html', {
        'sensors': sensors,
        'data_js': data_js
    })


def ajax_get_hourly_data(request):
    sensor_id = request.GET.get('sensorId', 1)
    return JsonResponse(hourly_data.get.get_data(sensor_id))


def ajax_update_hourly_data(request):
    return JsonResponse(hourly_data.update.update_data())


# Anomalies Dashboard
def show_anomalies(request):
    data_js = anomalies_data.get.get_data()
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
    return JsonResponse(anomalies_data.get.get_data(sensor_id, measure))


def ajax_update_anomalies(request):
    return JsonResponse(anomalies_data.update.update_data())
