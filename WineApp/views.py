from django.shortcuts import render

import WineApp.data.sensor_data as sensor_data
import WineApp.algorithms.exponential_smoothing as es
from WineApp.models import Wine


def index(request):
    wine = Wine.objects.get(pk=2)
    history = list(wine.weatherhistory_set.all()[:10])
    history.append('...')
    history += list(wine.weatherhistory_set.all().order_by('-pk')[:10])[::-1]
    return render(request, 'WineApp/index.html', {'list': history})


def download_sensor_data(request):
    pressione = sensor_data.update()
    return render(request, 'WineApp/download.html', {'dati': pressione})


def update_daily_sensor_data(request):
    data = sensor_data.update_daily_data()
    return render(request, 'WineApp/index.html', {'list': data})


def prediction(request, field):
    pred, actual, dates = es.exponential_smoothing(field)
    data = {'prediction': pred, 'actual': actual, 'dates': dates}
    return render(request, 'WineApp/predict.html', data)

