from itertools import groupby

from WineApp.data.utils import get_last_update, get_date_interval
from WineApp.models import Sensor, Prediction


def get_data(sensor_id: int = 0) -> dict:
    if sensor_id == 0 or sensor_id == '0':
        sensor = {'id': 0, 'name': 'Tutti i sensori', 'icon': 'fas fa-search', 'unit': ''}
        predictions = Prediction.objects
    else:
        sensor = Sensor.objects.get(pk=sensor_id)
        predictions = sensor.prediction_set
        sensor = sensor.to_js()
    predictions = predictions.filter(date__gte='2019-07-17').order_by('date')

    if not predictions:
        return {
            'lastUpdate': get_last_update('prediction'),
            'sensor': sensor,
            'error': 'No data'
        }

    last_date = predictions.last().date
    anomalies_all = predictions.filter(anomaly=True).values('date', 'sensor__name', 'measure', 'method',
                                                            'actual', 'prediction')
    anomalies_aggr = []
    for key, group_iter in groupby(anomalies_all, key=lambda x: (x['date'], x['sensor__name'], x['measure'])):
        group = list(group_iter)
        higher = sum(g['actual'] > g['prediction'] for g in group)
        lower = len(group) - higher

        anomalies_aggr.append({'date': key[0],
                               'sensor': key[1] + ' ' + key[2],
                               'higher': higher >= lower,
                               'gravity': len(group)})

    anomalies_date = []
    for key, group_iter in groupby(anomalies_aggr, key=lambda x: x['date']):
        group = list(group_iter)
        anomalies_date.append({'date': key,
                               'minor': [(g['sensor'], g['higher']) for g in group if g['gravity'] == 1],
                               'medium': [(g['sensor'], g['higher']) for g in group if g['gravity'] == 2],
                               'major': [(g['sensor'], g['higher']) for g in group if g['gravity'] == 3]})

    # Cards
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
        'sensor': sensor,
        'allAnomalies': anomalies_date,
        'anomaliesStats': anomalies_stats
    }
