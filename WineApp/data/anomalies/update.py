import os
import threading
from datetime import datetime, timedelta

from keras.models import load_model

import WineApp.data.algorithms as algorithms
import WineApp.data.daily as daily_data
import WineApp.data.daily.update
from WineApp.data.utils import get_last_update
from WineApp.models import LastUpdate, PredictionMethod, Sensor, Prediction, PredictionParams

semaphore = threading.Lock()
thread_data = {}


# Multi thread update
def update_data() -> dict:
    global thread_data
    updating = semaphore.locked()
    semaphore.acquire()
    try:
        if not updating:
            thread_data = _update_data()
    finally:
        semaphore.release()
    return thread_data


def _update_data() -> dict:
    if get_last_update('daily')['date'] != 'oggi':
        daily_data.update.update_data()
    reset_methods = PredictionMethod.objects.filter(reset=True)
    if get_last_update('prediction')['date'] != 'oggi' or reset_methods:
        predictions = _update_prediction_data()
        removed = 0
        for method in reset_methods:
            old_predictions = method.prediction_set.all()
            removed = removed + old_predictions.count()
            old_predictions.delete()
            # method.reset = False
            # method.save()
        Prediction.objects.bulk_create(predictions)
        LastUpdate.objects.update_or_create(type='prediction', defaults={'time': datetime.now()})
        return {'updated': removed, 'created': len(predictions) - removed}

    return {'created': 0}


def _update_prediction_data():
    predictions = []
    methods = PredictionMethod.objects.all()
    for sensor in Sensor.objects.all():
        for measure in sensor.get_prediction_measures():
            for method in methods:
                if method.reset:
                    saved_predictions = None
                else:
                    saved_predictions = Prediction.objects.filter(sensor=sensor, measure=measure,
                                                                  method=method).order_by('date')
                if saved_predictions:
                    last = saved_predictions.last()
                else:
                    last = Prediction(date=sensor.startTestSet, mean=0, var=0, count=0)
                if last.date != datetime.now().date() - timedelta(days=1):
                    train_set, test_set, date_set = _get_series(sensor, measure)
                    print(method.name + ' ' + str(sensor) + ' ' + measure)

                    params = method.get_params()
                    if PredictionParams.objects.filter(sensor=sensor, method=method).exists():
                        params.update(PredictionParams.objects.get(sensor=sensor, method=method).get_params())

                    model_filename = 'WineApp/models/' + method.name + '/' + sensor.name + ' ' + measure + '.h5'
                    if params.get('reset_models', False) and os.path.isfile(model_filename):
                        os.remove(model_filename)

                    if os.path.isfile(model_filename):
                        params['model'] = load_model(model_filename)

                    forecast, model = getattr(algorithms, method.name.lower())(train_set, test_set, params)

                    if model and not os.path.isfile(model_filename):
                        model.save(model_filename)

                    if len(forecast) == len(date_set):
                        for i in range(date_set.index(last.date) + 1, len(date_set)):
                            new = Prediction(date=date_set[i], sensor=sensor, measure=measure,
                                             actual=test_set[i], prediction=forecast[i], method=method)
                            new.check_limits()
                            algorithms.detect_anomaly(last, new, params)
                            predictions.append(new)
                            last = new
                    else:
                        print('Forecast len error: ' + str(len(forecast)) + '/' + str(len(date_set)))
    return predictions


def _get_series(sensor: Sensor, measure: str):
    train_set = sensor.dailydata_set.filter(date__lt=sensor.startTestSet).order_by('date')
    test_set = sensor.dailydata_set.filter(date__gte=sensor.startTestSet, date__lt=datetime.now().date()).order_by(
        'date')

    date_set = list(test_set.values_list('date', flat=True))
    train_set = list(train_set.values_list(measure, flat=True))
    test_set = list(test_set.values_list(measure, flat=True))
    return train_set, test_set, date_set
