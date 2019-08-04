import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from WineApp.data.sensor_data import get_series
from WineApp.algorithms.anomaly_detection import detect_anomalies


# todo scomporre database con anomaly, mean, var
# todo nella tabella dei sensori: id, name, seasonal, parametri modello
def exponential_smoothing(field, measure):
    train, test, seasonal, test_dates = get_series(field, measure)

    plt.title('Train Set')
    plt.plot(train)
    plt.show()
    plt.title('Test Set')
    plt.plot(test)
    plt.show()

    normal = normal_exponential_smoothing(train, seasonal, test)
    # Con il test così lungo la versione iterativa ci mette molto tempo
    # iterative = iterative_exponential_smoothing(train, seasonal, test)

    error = [test[i] - normal[i] for i in range(0, len(test))]
    anomaly1, anomaly2, anomaly3 = detect_anomalies(error, normal)
    # anomaly1_1, anomaly2_1, anomaly3_1 = detect_anomalies(test, iterative)

    title = 'Exp ' + str(0.45) + ' ' + str(0.6) + ' ' + field + measure
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
    fit_model = model.fit(smoothing_seasonal=0.8, smoothing_level=0.1)
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
