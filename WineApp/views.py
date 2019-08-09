import time
from datetime import datetime

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
    data, sensor, values, diff, last_month_mean, week_avg = sensor_data.get_daily_data()
    data_js = _daily_data_js(data, sensor, values, diff, last_month_mean, week_avg)
    data_js['ajax_url'] = reverse('WineApp:ajax.getDailyData')
    data_js['update_url'] = reverse('WineApp:ajax.updateDailyData')
    return render(request, 'WineApp/daily_data.html', {
        'sensors': Sensor.objects.all(),
        'data_js': data_js
    })


# Ajax
def get_daily_data(request, info=None):
    sensor_id = request.GET.get('sensor_id', 1)
    data, sensor, values, diff, last_month_mean, week_avg = sensor_data.get_daily_data(sensor_id)
    return JsonResponse(_daily_data_js(data, sensor, values, diff, last_month_mean, week_avg, info))


def _daily_data_js(data, sensor, values, diff, last_month_mean, week_avg, info=None):
    return {
        'data': data,
        'last': values[-1],
        'lastMonth': values[-31:],
        'diff': diff,
        'monthMean': last_month_mean,
        'weekMean': week_avg,
        'update': datetime.now().strftime('Oggi %H:%M'),
        'yesterday': values[-2],
        'info': info or '',
        'sensor': {'tot': sensor.tot, 'values': sensor.values, 'id': sensor.id, 'name': sensor.name,
                   'unit': sensor.unit, 'icon': sensor.icon}
    }


def ajax_update_daily_data(request):
    start = time.time()
    info = sensor_data.update_daily_data()
    end = time.time()
    print(end - start)
    return get_daily_data(request, info)


def update_daily_data(request):
    start = time.time()
    data = sensor_data.update_daily_data()
    # data = []
    # from WineApp.data.import_data import import_daily_data
    # import_daily_data()
    end = time.time()
    data.append('Time: ' + str(end - start))
    print(end - start)
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
