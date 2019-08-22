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

    # Charts
    last_date = predictions.last().date
    methods = PredictionMethod.objects.all()
    last_month = {}
    for method in methods:
        method_data = predictions.filter(method=method).values('date', 'actual', 'prediction', 'limit')
        method_last_month = get_date_interval(method_data, last_date, 30)
        for prediction in method_last_month:
            prediction['upperLimit'] = prediction['prediction'] + prediction['limit']
            prediction['lowerLimit'] = prediction['prediction'] - prediction['limit']
            del prediction['limit']
            prediction['error'] = prediction['actual'] - prediction['prediction']
        last_month[method.name.lower()] = [list(elem.values()) for elem in method_last_month]

    all_data = predictions.values('date', 'actual').distinct()

    anomalies_all = predictions.filter(anomaly=True).values('date', 'method__name')
    anomalies_aggr = []
    for key, group_iter in groupby(anomalies_all, key=lambda x: x['date']):
        group = list(group_iter)
        anomalies_aggr.append([key, len(group), ', '.join([e['method__name'] for e in group])])

    # Cards
    return {
        'lastUpdate': get_last_update('prediction'),
        'sensor': sensor.to_js(),
        'measure': measure,
        'methods': [e.name for e in methods],
        'allData': [list(elem.values()) for elem in all_data],
        'allAnomalies': anomalies_aggr,
        'lastMonth': last_month,
    }
