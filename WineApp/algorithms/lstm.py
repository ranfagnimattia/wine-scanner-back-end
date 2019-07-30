import statistics

import math
import matplotlib.pyplot as plt
import numpy as np
from django.http import Http404
from keras.layers import Dense
from keras.layers import LSTM
from keras.models import Sequential
from pandas import DataFrame
from pandas import Series
from pandas import concat
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

from WineApp.models import SensorHistory, DailySensorData


def lstm(field):
    train, test, seasonal, test_dates = _get_series(field)
    plt.plot(train)
    plt.show()

    normal = normal_lstm(train, seasonal, test)

    anomaly1_1, anomaly2_1, anomaly3_1 = detect_anomalies(test, normal)

    title = 'LSTM 30 32 1 10 ' + field
    plt.figure(figsize=(12, 7), dpi=200)
    plt.title(title)
    plt.plot(test, '#000000', label='Actual')
    plt.plot(normal, '#ebcc34', label='LSTM')
    plt.plot(anomaly1_1, 'og', markersize=7)
    plt.plot(anomaly2_1, 'oy', markersize=5)
    plt.plot(anomaly3_1, 'om', markersize=3)

    plt.legend()
    plt.savefig(title + '.png')
    plt.show()
    return normal, test, test_dates


# frame a sequence as a supervised learning problem
def timeseries_to_supervised(data, lag=1):
    df = DataFrame(data)
    columns = [df.shift(i) for i in range(1, lag + 1)]
    columns.append(df)
    df = concat(columns, axis=1)
    df = df.iloc[1:]
    df.fillna(0, inplace=True)
    return df.values


# create a differenced series
def difference(dataset, interval=1):
    diff = list()
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i - interval]
        diff.append(value)
    return Series(diff)


# invert differenced value
def inverse_difference(history, yhat, interval=1):
    return yhat + history[-interval]


# scale train and test data to [-1, 1]
def scale(train, test):
    # fit scaler
    scaler = MinMaxScaler(feature_range=(-1, 1))
    scaler = scaler.fit(train)
    # transform train
    train = train.reshape(train.shape[0], train.shape[1])
    train_scaled = scaler.transform(train)
    # transform test
    test = test.reshape(test.shape[0], test.shape[1])
    test_scaled = scaler.transform(test)
    return scaler, train_scaled, test_scaled


# inverse scaling for a forecasted value
def invert_scale(scaler, X, value):
    new_row = [x for x in X] + [value]
    array = np.array(new_row)
    array = array.reshape(1, len(array))
    inverted = scaler.inverse_transform(array)
    return inverted[0, -1]


# fit an LSTM network to training data
def fit_lstm(train, batch_size, nb_epoch, neurons):
    X, y = train[:, 0:-1], train[:, -1]
    X = X.reshape(X.shape[0], 1, X.shape[1])
    model = Sequential()
    model.add(LSTM(neurons, batch_input_shape=(batch_size, X.shape[1], X.shape[2]), stateful=True))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    for i in range(nb_epoch):
        model.fit(X, y, epochs=1, batch_size=batch_size, verbose=0, shuffle=False)
        model.reset_states()
    return model


# make a one-step forecast
def forecast_lstm(model, batch_size, X):
    X = X.reshape(1, 1, len(X))
    yhat = model.predict(X, batch_size=batch_size)
    return yhat[0, 0]


def memory_lstm(train, seasonal, test):
    np.random.seed(7)

    train_log = np.log10(train[-900:])
    test_log = np.log10(train[-1:] + test)

    train_lstm = timeseries_to_supervised(train_log, 1)
    test_lstm = timeseries_to_supervised(test_log, 1)

    # actual_vals = train[-300:] + test
    # actual_log = np.log10(actual_vals)
    # supervised_values = timeseries_to_supervised(actual_log, 1)
    # # split data into train and test-sets
    # train_lstm, test_lstm = supervised_values[0:-10], supervised_values[-10:]

    # transform the scale of the data
    scaler, train_scaled_lstm, test_scaled_lstm = scale(train_lstm, test_lstm)
    # fit the model                 batch,Epoch=850,Neurons
    lstm_model = fit_lstm(train_scaled_lstm, 1, 50, 3)
    # forecast the entire training dataset to build up state for forecasting
    train_reshaped = train_scaled_lstm[:, 0].reshape(len(train_scaled_lstm), 1, 1)

    # lstm_model.predict(train_reshaped, batch_size=1)
    # walk-forward validation on the test data
    predictions = list()
    for i in range(len(test_scaled_lstm)):
        # make one-step forecast
        X, y = test_scaled_lstm[i, 0:-1], test_scaled_lstm[i, -1]
        yhat = forecast_lstm(lstm_model, 1, X)
        # invert scaling
        yhat = invert_scale(scaler, X, yhat)
        # invert differencing
        # yhat = inverse_difference(raw_values, yhat, len(test_scaled)+1-i)
        # store forecast
        predictions.append(10 ** yhat)
        # expected = actual_log[len(train_lstm) + i]
    return predictions


def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back):
        a = dataset[i:(i + look_back)]
        dataX.append(a)
        dataY.append([dataset[i + look_back]])
    return np.array(dataX), np.array(dataY)


def normal_lstm(train, seasonal, test):
    # fix random seed for reproducibility
    np.random.seed(7)

    look_back = 30
    neurons = 32
    batch_size = 1
    epochs = 10
    dataset = np.array(train + test)
    dataset = dataset.reshape(-1, 1)
    # normalize the dataset
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    # split into train and test sets
    train, test = dataset[0:-len(test), 0], dataset[-len(test) - look_back:, 0]
    # reshape into X=t and Y=t+1
    trainX, trainY = create_dataset(train, look_back)
    testX, testY = create_dataset(test, look_back)
    # reshape input to be [samples, time steps, features]
    trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(neurons, input_shape=(1, look_back)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, epochs=epochs, batch_size=batch_size, verbose=2)
    # make predictions
    trainPredict = model.predict(trainX)
    testPredict = model.predict(testX)
    # invert predictions
    trainPredict = scaler.inverse_transform(trainPredict)
    trainY = scaler.inverse_transform(trainY)
    testPredict = scaler.inverse_transform(testPredict)
    testY = scaler.inverse_transform(testY)
    # calculate root mean squared error
    trainScore = math.sqrt(mean_squared_error(trainY[:, 0], trainPredict[:, 0]))
    print('Train Score: %.2f RMSE' % (trainScore))
    testScore = math.sqrt(mean_squared_error(testY[:, 0], testPredict[:, 0]))
    print('Test Score: %.2f RMSE' % (testScore))
    # shift train predictions for plotting
    # trainPredictPlot = np.empty_like(dataset)
    # trainPredictPlot[:, :] = np.nan
    # trainPredictPlot[look_back:len(trainPredict) + look_back, :] = trainPredict
    # # shift test predictions for plotting
    # testPredictPlot = np.empty_like(dataset)
    # testPredictPlot[:, :] = np.nan
    # testPredictPlot[len(trainPredict) + (look_back * 2) + 1:len(dataset) - 1, :] = testPredict
    # # plot baseline and predictions
    # plt.plot(scaler.inverse_transform(dataset))
    # plt.plot(trainPredictPlot)
    # plt.plot(testPredictPlot)
    # plt.show()
    predict = testPredict.reshape(1, -1)
    return predict[0]


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
