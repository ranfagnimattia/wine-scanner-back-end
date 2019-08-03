import statistics

import math
import matplotlib.pyplot as plt
import numpy as np
from WineApp.data.sensor_data import _get_series
from statsmodels.tsa.holtwinters import ExponentialSmoothing




# todo scomporre database con anomaly, mean, var
# todo nella tabella dei sensori: id, name, seasonal, parametri modello
def exponential_smoothing(field, measure):

    train, test, seasonal, test_dates = _get_series(field,measure)

    plt.title('Train Set')
    plt.plot(train)
    plt.show()
    plt.title('Test Set')
    plt.plot(test)
    plt.show()

    normal = normal_exponential_smoothing(train, seasonal, test)
    # Con il test così lungo la versione iterativa ci mette molto tempo
    # iterative = iterative_exponential_smoothing(train, seasonal, test)

    anomaly1, anomaly2, anomaly3 = detect_anomalies(test, normal)
    # anomaly1_1, anomaly2_1, anomaly3_1 = detect_anomalies(test, iterative)

    title = 'Exp ' + str(0.45) + ' ' + str(0.6) + ' ' + field+measure
    plt.figure(figsize=(12, 7), dpi=200)
    plt.title(title)
    plt.plot(test, '#000000', label='Actual')
    plt.plot(normal, '#eb4634', label='Pred normal')
    # plt.plot(iterative, '#ebcc34', label='Pred iterative')
    plt.plot(anomaly1, 'og', label='std', markersize=7)
    plt.plot(anomaly2, 'oy', label='stdev_corr', markersize=5)
    plt.plot(anomaly3, 'om', label='stdev welford', markersize=3)
    # plt.plot(anomaly1_1, 'og', markersize=7)
    # plt.plot(anomaly2_1, 'oy', markersize=5)
    # plt.plot(anomaly3_1, 'om', markersize=3)

    plt.legend()
    # plt.savefig(title + '.png')
    plt.show()
    return normal, test, test_dates


def normal_exponential_smoothing(train, seasonal, test):
    if seasonal:
        model = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=365)
    else:
        model = ExponentialSmoothing(train, trend='add', seasonal=None)
    fit_model = model.fit(smoothing_seasonal=0.7,smoothing_level=0.2)
    return fit_model.forecast(len(test))


def iterative_exponential_smoothing(train, seasonal, test):
    pred_list = []

    for point in test:
        if seasonal:
            model = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=365)
        else:
            model = ExponentialSmoothing(train, trend='add', seasonal=None)
        fit_model = model.fit(smoothing_seasonal=0.45, smoothing_level=0.2)
        pred_list.extend(fit_model.forecast())
        train.append(point)

    return pred_list

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
