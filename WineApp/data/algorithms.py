import math
import numpy as np
from keras.layers import Dense
from keras.layers import LSTM
from keras.models import Sequential
from keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose

from WineApp.models import Prediction


def detect_anomaly(last: Prediction, new: Prediction, params):
    error = new.actual - new.prediction
    # stdev_corr
    new_mean, new_var = _update_stats(last.mean, last.var, error, last.count + 1)
    if last.count == 0:
        new.limit = 100
    else:
        new.limit = params['k'] * math.sqrt(new_var / last.count)
    if abs(error) > new.limit:
        new.mean = last.mean
        new.var = last.var
        new.count = last.count
        new.anomaly = True
    else:
        new.mean = new_mean
        new.var = new_var
        new.count = last.count + 1
        new.anomaly = False


def _update_stats(m, v, val, n):
    mean = m + (1 / n) * (val - m)
    var = v + (val - m) * (val - mean)
    return mean, var


def exp(train_set, test_set, params):
    model = ExponentialSmoothing(train_set, trend='add', seasonal='add', seasonal_periods=365)
    fit_model = model.fit(smoothing_seasonal=params['smoothing_seasonal'], smoothing_level=params['smoothing_level'])
    return fit_model.forecast(len(test_set))


def stl(train_set, test_set, params):
    complete_set = train_set + test_set
    decompose = seasonal_decompose(complete_set, model='additive', two_sided=False, freq=365)
    forecast = [(decompose.seasonal[i] + decompose.trend[i]) for i in range(0, len(decompose.seasonal)) if
                not np.isnan(decompose.trend[i])]
    return forecast[-len(test_set):]


def lstm(train_set, test_set, params):
    # fix random seed for reproducibility
    np.random.seed(7)

    dataset = np.array(train_set + test_set)
    dataset = dataset.reshape(-1, 1)
    # normalize the dataset
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    # split into train and test sets
    train, test = dataset[0:-len(test_set), 0], dataset[-len(test_set) - params['lookback']:, 0]
    # reshape into X=t and Y=t+1
    train_x, train_y = _create_dataset(train, params['lookback'])
    test_x, test_y = _create_dataset(test, params['lookback'])
    # reshape input to be [samples, time steps, features]
    train_x = np.reshape(train_x, (train_x.shape[0], 1, train_x.shape[1]))
    test_x = np.reshape(test_x, (test_x.shape[0], 1, test_x.shape[1]))
    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(params['neurons'], input_shape=(1, params['lookback'])))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer=Adam(lr=0.0001))
    model.fit(train_x, train_y, epochs=params['epochs'], batch_size=params['batchsize'], verbose=2,
              validation_data=[test_x, test_y])
    # make predictions
    test_predict = model.predict(test_x)
    # invert predictions
    forecast = scaler.inverse_transform(test_predict).reshape(1, -1)
    return forecast[0]


def _create_dataset(dataset, look_back=1):
    data_x, data_y = [], []
    for i in range(len(dataset) - look_back):
        a = dataset[i:(i + look_back)]
        data_x.append(a)
        data_y.append([dataset[i + look_back]])
    return np.array(data_x), np.array(data_y)
