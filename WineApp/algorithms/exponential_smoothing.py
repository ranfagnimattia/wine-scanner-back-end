import statistics
import math
import matplotlib.pyplot as plt
import numpy as np
from django.http import Http404
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from WineApp.models import SensorHistory, DailySensorData


# todo scomporre database con anomaly, mean, var
# todo nella tabella dei sensori: id, name, seasonal, parametri modello
# todo stl, lstm
def exponential_smoothing(field):
    train, test, seasonal, test_dates = _get_series(field)
    plt.plot(train)
    plt.show()

    normal = normal_exponential_smoothing(train, seasonal)
    iterative = iterative_exponential_smoothing(train, seasonal, test)

    # title = "Normal " + str(fit_model.params['smoothing_seasonal']) + " " + \
    #         str(fit_model.params['smoothing_level']) + " " + field

    anomaly1, anomaly2, anomaly3 = detect_anomalies(test, normal)
    anomaly1_1, anomaly2_1, anomaly3_1 = detect_anomalies(test, iterative)

    title = str(0.45) + ' ' + str(0.6) + ' ' + field
    plt.title(title)
    plt.plot(test, '#000000', label='Actual')
    plt.plot(normal, '#eb4634', label='Pred normal')
    plt.plot(iterative, '#ebcc34', label='Pred iterative')
    plt.plot(anomaly1, 'og', label='std', markersize=17)
    plt.plot(anomaly2, 'vy', label='stdev_corr', markersize=12)
    plt.plot(anomaly3, 'sm', label='stdev welford', markersize=5)
    plt.plot(anomaly1_1, 'og', markersize=17)
    plt.plot(anomaly2_1, 'vy', markersize=12)
    plt.plot(anomaly3_1, 'sm', markersize=5)

    plt.legend()
    plt.show()
    return normal, test, test_dates


def normal_exponential_smoothing(train, seasonal):
    if seasonal:
        model = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=365)
    else:
        model = ExponentialSmoothing(train, trend='add', seasonal=None)
    fit_model = model.fit(smoothing_seasonal=0.45, smoothing_level=0.6)
    return fit_model.forecast(10)


def iterative_exponential_smoothing(train, seasonal, test):
    pred_list = []

    for point in test:
        if seasonal:
            model = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=365)
        else:
            model = ExponentialSmoothing(train, trend='add', seasonal=None)
        fit_model = model.fit(smoothing_seasonal=0.45, smoothing_level=0.6)
        pred_list.extend(fit_model.forecast())
        train.append(point)

    return pred_list


def _get_series(field: str):
    seasonal_fields = ['airTemperatureAvg', 'airTemperatureMin', 'airTemperatureMax', 'rainAvg',
                       'windSpeedAvg', 'windSpeedMax', 'dewPointAvg', 'dewPointMax', 'dewPointMin']
    if field not in seasonal_fields:
        raise Http404("Field does not exist")
    if field.startswith('dewPoint'):
        train_set = SensorHistory.objects.filter(date__gte='2017-03-12')
    else:
        train_set = SensorHistory.objects.all()
    train_list = list(train_set.values_list(field, flat=True))

    test_set = DailySensorData.objects.all()
    test_list = list(test_set.values_list(field, flat=True))

    return train_list, test_list, field in seasonal_fields, test_set.values_list('date', flat=True)


def detect_anomalies(actual, prediction):
    error = [actual[i] - prediction[i] for i in range(0, len(actual))]
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
            anomaly1.append(prediction[i])
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
            anomaly2.append(prediction[i])
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
            anomaly3.append(prediction[i])
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


def update(m, v, val, n):
    mean = m + (1 / n) * (val - m)
    var = v + (val - m) * (val - mean)
    return mean, var
