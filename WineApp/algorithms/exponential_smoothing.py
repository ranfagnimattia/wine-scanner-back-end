import matplotlib.pyplot as plt
import math
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from WineApp.models import SensorHistory, DailySensorData


def exponential_smoothing(field):
    train, test, test_dates = _get_series(field)
    plt.plot(train)
    plt.show()
    ss = 0.45
    sl = 0.6
    if field == 'airTemperatureAvg' or field == 'dewPointAvg' \
            or field == 'airTemperatureMax' or field == 'airTemperatureMin':
        model = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=365)
    else:
        model = ExponentialSmoothing(train, trend='add', seasonal=None)
    fit_model = model.fit(smoothing_seasonal=ss, smoothing_level=sl)

    title = "" + str(ss) + " " + str(sl) + " " + field

    pred = fit_model.forecast(10)

    anomaly1, anomaly2, anomaly3 = detect_anomalies(test, pred)

    plt.title(title)
    plt.plot(pred, '-r', label='Predictions')
    plt.plot(test, '-b', label='Actual')
    # Plot anomalies
    plt.plot(anomaly1, 'og', label='std', markersize=17)
    plt.plot(anomaly2, 'vy', label='stdev_corr', markersize=12)
    plt.plot(anomaly3, 'sm', label='stdev welford', markersize=5)
    plt.legend()
    plt.show()
    actual = test
    return pred, actual, test_dates


def _get_series(field):
    data = SensorHistory.objects.filter(date__gte='2017-03-12', date__lte='2019-07-16')
    train_values = data.values_list(field, flat=True)

    data = DailySensorData.objects.filter()
    dates = data.values_list('date', flat=True)
    test_values = data.values_list(field, flat=True)

    train_values = list(train_values)
    test_values = list(test_values)

    return train_values, test_values, dates


def detect_anomalies(actual, prediction):
    error = actual - prediction
    anomaly1 = []
    anomaly2 = []
    anomaly3 = []

    # stddev calculate at the beginning
    std = error.std()
    print(std)
    for i in range(0, len(error)):
        if abs(error[i]) > 3 * std:
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
        std = math.sqrt(new_var / i)
        if abs(error[i]) > 3 * std:
            anomaly2.append(actual[i])
        else:
            anomaly2.append(np.NaN)
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
        if abs(error[i]) > 3 * std:
            anomaly3.append(actual[i])
        else:
            anomaly3.append(np.NaN)
    print(std)

    plt.plot(error, '-g')
    plt.title('Error')
    plt.show()
    return anomaly1, anomaly2, anomaly3


def update(m, v, val, n):
    mean = m + (1 / n) * (val - m)
    var = v + (val - m) * (val - mean)
    return mean, var
