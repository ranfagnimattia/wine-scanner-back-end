import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from WineApp.algorithms.anomaly_detection import detect_anomalies
import numpy as np


def stl(train_set, test_set):
    # Code for Test in Python Console
    """
        from WineApp.models import Sensor
        from WineApp.algorithms import seasonal_decompose
        from WineApp.data import sensor_data
        test,train,date = sensor_data.get_series(Sensor.objects.get(pk=1),'avg')
        seasonal_decompose.stl(train,test,{})
    """
    complete_set = train_set + test_set
    decompose = seasonal_decompose(complete_set, model='additive', two_sided=False, freq=365)

    null_values = np.sum(np.isnan(decompose.resid))

    forecast = [(decompose.seasonal[i] + decompose.trend[i]) for i in range(0, len(decompose.seasonal)) if
                not np.isnan(decompose.trend[i])]

    # Eliminare poi
    decompose.plot()
    plt.show()
    error = [x for x in decompose.resid if not np.isnan(x)]
    anomaly1, anomaly2, anomaly3 = detect_anomalies(error, complete_set[null_values:])
    title = 'Seasonal Decompose'
    plt.figure(figsize=(12, 7), dpi=200)
    plt.title(title)
    plt.plot(complete_set[null_values:], '#000000', label='Actual')
    plt.plot(forecast, '#eb4634', label='Prediction')
    plt.plot(anomaly1, 'og', label='std', markersize=7)
    plt.plot(anomaly2, 'oy', label='stdev_corr', markersize=5)
    plt.plot(anomaly3, 'om', label='stdev welford', markersize=3)
    plt.legend()
    plt.show()

    return forecast
