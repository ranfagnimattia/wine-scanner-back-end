from itertools import groupby

from WineApp.data.utils import get_last_update, get_date_interval
from WineApp.models import Sensor, PredictionMethod


def get_data(sensor_id: int = 1, measure: str = 'avg') -> dict:
    sensor = Sensor.objects.get(pk=sensor_id)
    predictions = sensor.prediction_set.filter(date__gte='2019-07-17', measure=measure).order_by('date')

    if not predictions:
        return {
            'lastUpdate': get_last_update('prediction'),
            'sensor': sensor.to_js(),
            'measure': measure,
            'error': 'No data'
        }

    last_date = predictions.last().date
    methods = PredictionMethod.objects.all()
    last_month = {}
    all_data_prediction = {}
    method_stats = {}
    for method in methods:
        method_predictions = predictions.filter(method=method)
        method_data = method_predictions.values('date', 'actual', 'prediction', 'limit',
                                                'sensor__min', 'sensor__max')
        method_last_month = get_date_interval(method_data, last_date, 30)
        for prediction in method_last_month:
            prediction['upperLimit'] = prediction['prediction'] + prediction['limit']
            if prediction['sensor__max'] is not None and prediction['upperLimit'] > prediction['sensor__max']:
                prediction['upperLimit'] = prediction['sensor__max']
            prediction['lowerLimit'] = prediction['prediction'] - prediction['limit']
            if prediction['sensor__min'] is not None and prediction['lowerLimit'] < prediction['sensor__min']:
                prediction['lowerLimit'] = prediction['sensor__min']

            del prediction['limit']
            del prediction['sensor__min']
            del prediction['sensor__max']
            prediction['error'] = prediction['actual'] - prediction['prediction']
        last_month[method.name.lower()] = [list(elem.values()) for elem in method_last_month]

        for prediction in method_data:
            prediction['upperLimit'] = prediction['prediction'] + prediction['limit']
            if prediction['sensor__max'] is not None and prediction['upperLimit'] > prediction['sensor__max']:
                prediction['upperLimit'] = prediction['sensor__max']
            prediction['lowerLimit'] = prediction['prediction'] - prediction['limit']
            if prediction['sensor__min'] is not None and prediction['lowerLimit'] < prediction['sensor__min']:
                prediction['lowerLimit'] = prediction['sensor__min']

            del prediction['limit']
            del prediction['sensor__min']
            del prediction['sensor__max']
            prediction['error'] = prediction['actual'] - prediction['prediction']
        all_data_prediction[method.name.lower()] = [list(elem.values()) for elem in method_data]

        anomalies = method_predictions.filter(anomaly=True)
        method_stats[method.name.lower()] = {
            'tot': anomalies.count(),
            'lastMonth': get_date_interval(anomalies, last_date, 30).count(),
            'mse': method_predictions.last().get_mse()
        }

    all_data = predictions.values('date', 'actual').distinct()

    anomalies_all = predictions.filter(anomaly=True).values('date', 'method__name', 'actual', 'prediction')
    anomalies_aggr = []
    for key, group_iter in groupby(anomalies_all, key=lambda x: x['date']):
        group = list(group_iter)
        methods_info = [(e['method__name'], e['actual'] > e['prediction']) for e in group]
        anomalies_aggr.append({'date': key, 'gravity': len(group), 'methods': methods_info})

    anomalies_last_month = get_date_interval(predictions.filter(anomaly=True), last_date, 30) \
        .values('date', 'method__name')
    anomalies_last_month_aggr = [{'date': key, 'gravity': len(list(group_iter))} for key, group_iter in
                                 groupby(anomalies_last_month, key=lambda x: x['date'])]

    anomalies_stats = {
        'lastMonth': {
            'minor': sum(i['gravity'] == 1 for i in anomalies_last_month_aggr),
            'medium': sum(i['gravity'] == 2 for i in anomalies_last_month_aggr),
            'major': sum(i['gravity'] == 3 for i in anomalies_last_month_aggr)
        },
        'tot': {
            'minor': sum(i['gravity'] == 1 for i in anomalies_aggr),
            'medium': sum(i['gravity'] == 2 for i in anomalies_aggr),
            'major': sum(i['gravity'] == 3 for i in anomalies_aggr)
        }
    }

    return {
        'lastUpdate': get_last_update('prediction'),
        'sensor': sensor.to_js(),
        'measure': measure,
        'methods': [e.name for e in methods],
        'allData': [list(elem.values()) for elem in all_data],
        'allDataPrediction': all_data_prediction,
        'allAnomalies': anomalies_aggr,
        'lastMonth': last_month,
        'methodStats': method_stats,
        'anomaliesStats': anomalies_stats
    }
