from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

import WineApp.algorithms.correlation as cor
import WineApp.algorithms.exponential_smoothing as es
import WineApp.algorithms.lstm as ls
import WineApp.algorithms.seasonal_decompose as sd
import WineApp.data.import_data as import_data
import WineApp.data.sensor_data as sensor_data
# Include the `fusioncharts.py` file that contains functions to embed the charts.
from WineApp.fusioncharts import FusionCharts
from WineApp.fusioncharts import FusionTable
from WineApp.fusioncharts import TimeSeries
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
    schema = '''[
        {
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        },
        {
            name: "Avg",
            type: "number"
        },
        { 
            name: "Min",
            type: "number"
        },
        { 
            name: "Max",
            type: "number"
        }]'''
    data = import_data.show_data()
    fusionTable = FusionTable(schema, data)
    timeSeries = TimeSeries(fusionTable)

    timeSeries.AddAttribute('chart', '{}')
    timeSeries.AddAttribute('caption', '{"text":"Sales Analysis"}')
    timeSeries.AddAttribute('subcaption', '{"text":"Grocery"}')
    timeSeries.AddAttribute('yaxis',
                            '[{"plot":[{"value":"Avg"},{"value":"Min"},{"value":"Max"}],'
                            '"format":{"prefix":"$"},"title":"Avg Value"}]')

    # Create an object for the chart using the FusionCharts class constructor
    fcChart = FusionCharts("timeseries", "myFirstChart", 700, 450, "myFirstchart-container", "json", timeSeries)

    return render(request, 'WineApp/daily_data.html', {
        'sensors': Sensor.objects.all(),
        'data': {'schema': schema,
                 'data': data,
                 'ajaxUrl': reverse('WineApp:ajax.getDailyData')}
    })
    # return render(request, 'WineApp/daily_data.html', {
    #     'output': fcChart.render()
    # })


def get_daily_data(request):
    sensor_id = request.GET.get('sensor_id', 1)

    data = import_data.show_data(sensor_id)
    return JsonResponse({
        'data': {'data': data, 'id': sensor_id}
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
