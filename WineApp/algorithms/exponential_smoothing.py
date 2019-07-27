import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from WineApp.models import SensorHistory, DailySensorData


def exponential_smoothing(field):
    train, test, test_dates = _get_series(field)
    plt.plot(train)
    plt.show()
    ss = 0.45
    sl = 0.6
    if field == 'airTemperatureAvg' or field == 'dewPointAvg':
        model = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=365)
    else:
        model = ExponentialSmoothing(train, trend='add', seasonal=None)
    fit_model = model.fit(smoothing_seasonal=ss, smoothing_level=sl)

    title = ""+str(ss)+" "+str(sl)+" "+field

    pred = fit_model.forecast(10)
    plt.title(title)
    plt.plot(pred, '-r', label='Predictions')
    plt.plot(test, 'b', label='Actual')

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

    train_values = _convert_to_vector(train_values)
    test_values = _convert_to_vector(test_values)

    return train_values, test_values, dates


def _convert_to_vector(set):
    result = []
    for i in set:
        result.append(i)
    return result
