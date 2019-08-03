from django.shortcuts import render

import WineApp.algorithms.correlation as cor
import WineApp.algorithms.exponential_smoothing as es
import WineApp.algorithms.lstm as ls
import WineApp.algorithms.seasonal_decompose as sd
import WineApp.data.sensor_data as sensor_data
import WineApp.data.import_data as import_data


def index(request):
    history = []
    # wine = Wine.objects.get(pk=2)
    # history = list(wine.weatherhistory_set.all()[:10])
    # history.append('...')
    # history += list(wine.weatherhistory_set.all().order_by('-pk')[:10])[::-1]
    # history = import_history()
    return render(request, 'WineApp/index.html', {'list': history})


def show_data(request):
    import_data.show_data()
    return render(request, 'WineApp/download.html')


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
    pred, actual, dates = ls.lstm(field,measure)
    data = {'prediction': pred, 'actual': actual, 'dates': dates}
    return render(request, 'WineApp/predict.html', data)


def decompose(request, field):
    sd.stl(field)
    return render(request, 'WineApp/decompose.html')


def correlation(request):
    cor.correlation()
    return render(request, 'WineApp/correlation.html')
