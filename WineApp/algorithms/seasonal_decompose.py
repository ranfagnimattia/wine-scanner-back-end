import statistics

import math
import matplotlib.pyplot as plt
import numpy as np
from django.http import Http404
from statsmodels.tsa.seasonal import seasonal_decompose

from WineApp.models import WeatherHistory


def stl(field: str):
    values, dates = _get_series(field)
    decompose = seasonal_decompose(values, model='additive', freq=365)
    decompose.plot()
    plt.title(field)
    plt.show()
    error = decompose.resid
    # Reduce the size of the list because there are many NaN
    start, end = _get_limit(error)
    error = error[start:end + 1]
    values = values[start:end + 1]

    anomaly1, anomaly2, anomaly3 = detect_anomalies(error, values)

    title = 'STL '+field

    plt.figure(figsize=(12, 7), dpi=200)
    plt.title(title)
    plt.plot(values, '#000000', label='Actual')
    plt.plot(anomaly1, 'og', label='std', markersize=7)
    plt.plot(anomaly2, 'oy', label='stdev_corr', markersize=5)
    plt.plot(anomaly3, 'om', label='stdev welford', markersize=3)
    plt.legend()
    plt.savefig(title+'.png')
    plt.show()


def detect_anomalies(error, actual):
    absolute_error = [abs(error[i]) for i in range(0, len(error))]
    anomaly1 = []
    anomaly2 = []
    anomaly3 = []

    std1 = []
    std2 = []
    std3 = []

    k = 2.5

    # stddev calculate at the beginning
    std = statistics.stdev(error)
    for i in range(0, len(error)):
        std1.append(k * std)
        if abs(error[i]) > k * std:
            anomaly1.append(actual[i])
        else:
            anomaly1.append(np.NaN)
    print(std)

    # stdev_corr
    mean = 0
    var = 0
    count = 0
    for i in range(0, len(error)):
        new_mean, new_var = update(mean, var, error[i], count + 1)
        std = math.sqrt(new_var / count)
        if abs(error[i]) > k * std:
            anomaly2.append(actual[i])
            std2.append(std2[i - 1])
        else:
            anomaly2.append(np.NaN)
            std2.append(k * std)
            mean = new_mean
            var = new_var
            count = count + 1
    print(std)

    # stdev
    mean = 0
    var = 0
    for i in range(0, len(error)):
        mean, var = update(mean, var, error[i], i + 1)
        std = math.sqrt(var / i)
        std3.append(k * std)
        if abs(error[i]) > k * std:
            anomaly3.append(actual[i])
        else:
            anomaly3.append(np.NaN)
    print(std)

    plt.plot(absolute_error, '-k')
    plt.plot(std1, '--g', label='std')
    plt.plot(std2, '--y', label='stdev_corr', linewidth=3)
    plt.plot(std3, '--m', label='stdev_welford')
    plt.title('Absolute Error')
    plt.legend()
    plt.show()

    return anomaly1, anomaly2, anomaly3


def _get_limit(values):
    start = -1
    end = -1
    for i in range(0, len(values)):
        if not math.isnan(values[i]) and start == -1:
            start = i
        if not math.isnan(values[-(i + 1)]) and end == -1:
            end = len(values) - i - 1
    return start, end


def _get_series(field: str):
    seasonal_fields = ['airTemperatureAvg', 'airTemperatureMin', 'airTemperatureMax', 'rainAvg',
                       'windSpeedAvg', 'windSpeedMax', 'dewPointAvg', 'dewPointMax', 'dewPointMin']
    if field not in seasonal_fields:
        raise Http404("Field does not exist")
    if field.startswith('dewPoint'):
        train_set = WeatherHistory.objects.filter(date__gte='2017-03-12')
    else:
        train_set = WeatherHistory.objects.all()
    values_list = list(train_set.values_list(field, flat=True))
    dates_list = list(train_set.values_list('date', flat=True))

    return values_list, dates_list


def update(m, v, val, n):
    mean = m + (1 / n) * (val - m)
    var = v + (val - m) * (val - mean)
    return mean, var
