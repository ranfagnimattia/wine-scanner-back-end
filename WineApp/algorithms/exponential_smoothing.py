import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from WineApp.algorithms.anomaly_detection import detect_anomalies


# todo scomporre database con anomaly, mean, var
# todo nella tabella dei sensori: id, name, seasonal, parametri modello
def exponential_smoothing(train_set, test_set, param):
    # Code for Test in Python Console
    """
        from WineApp.models import Sensor
        from WineApp.algorithms import exponential_smoothing
        from WineApp.data import sensor_data
        param = {'smoothing_seasonal':0.8,'smoothing_level':0.1}
        test,train,date = sensor_data.get_series(Sensor.objects.get(pk=1),'avg')
        exponential_smoothing.exponential_smoothing(train,test,param)
    """
    model = ExponentialSmoothing(train_set, trend='add', seasonal='add', seasonal_periods=365)
    fit_model = model.fit(smoothing_seasonal=param['smoothing_seasonal'], smoothing_level=param['smoothing_level'])
    forecast = fit_model.forecast(len(test_set))

    # Eliminare poi
    error = [test_set[i] - forecast[i] for i in range(0, len(forecast))]
    anomaly1, anomaly2, anomaly3 = detect_anomalies(error, test_set)
    title = 'Exponential Smoothing SS: ' + str(param['smoothing_seasonal']) + ' SL: ' + str(param['smoothing_level'])
    plt.figure(figsize=(12, 7), dpi=200)
    plt.title(title)
    plt.plot(test_set, '#000000', label='Actual')
    plt.plot(forecast, '#eb4634', label='Prediction')
    plt.plot(anomaly1, 'og', label='std', markersize=7)
    plt.plot(anomaly2, 'oy', label='stdev_corr', markersize=5)
    plt.plot(anomaly3, 'om', label='stdev welford', markersize=3)
    plt.legend()
    plt.show()

    return forecast

# def normal_exponential_smoothing(train, seasonal, test):
#     if seasonal:
#         model = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=365)
#     else:
#         model = ExponentialSmoothing(train, trend='add', seasonal=None)
#     fit_model = model.fit(smoothing_seasonal=0.8, smoothing_level=0.1)
#     return fit_model.forecast(len(test))
#
#
# def iterative_exponential_smoothing(train, seasonal, test):
#     pred_list = []
#
#     for point in test:
#         if seasonal:
#             model = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=365)
#         else:
#             model = ExponentialSmoothing(train, trend='add', seasonal=None)
#         fit_model = model.fit(smoothing_seasonal=0.45, smoothing_level=0.2)
#         pred_list.extend(fit_model.forecast())
#         train.append(point)
#
#     return pred_list

# def exponential_smoothing(field, measure):
#     train, test, seasonal, test_dates = get_series(field, measure)
#
#     plt.title('Train Set')
#     plt.plot(train)
#     plt.show()
#     plt.title('Test Set')
#     plt.plot(test)
#     plt.show()
#
#     normal = normal_exponential_smoothing(train, seasonal, test)
#     # Con il test così lungo la versione iterativa ci mette molto tempo
#     # iterative = iterative_exponential_smoothing(train, seasonal, test)
#
#     error = [test[i] - normal[i] for i in range(0, len(test))]
#     anomaly1, anomaly2, anomaly3 = detect_anomalies(error, normal)
#     # anomaly1_1, anomaly2_1, anomaly3_1 = detect_anomalies(test, iterative)
#
#     title = 'Exp ' + str(0.45) + ' ' + str(0.6) + ' ' + field + measure
#     plt.figure(figsize=(12, 7), dpi=200)
#     plt.title(title)
#     plt.plot(test, '#000000', label='Actual')
#     plt.plot(normal, '#eb4634', label='Pred normal')
#     # plt.plot(iterative, '#ebcc34', label='Pred iterative')
#     plt.plot(anomaly1, 'og', label='std', markersize=7)
#     plt.plot(anomaly2, 'oy', label='stdev_corr', markersize=5)
#     plt.plot(anomaly3, 'om', label='stdev welford', markersize=3)
#     # plt.plot(anomaly1_1, 'og', markersize=7)
#     # plt.plot(anomaly2_1, 'oy', markersize=5)
#     # plt.plot(anomaly3_1, 'om', markersize=3)
#
#     plt.legend()
#     # plt.savefig(title + '.png')
#     plt.show()
#     return normal, test, test_dates
