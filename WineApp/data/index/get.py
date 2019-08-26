from itertools import groupby

import numpy as np

from WineApp.data.utils import get_last_update, sort_and_group
from WineApp.models import Sensor, Prediction


def get_data(sensor_id: int = 0) -> dict:
    if sensor_id == 0 or sensor_id == '0':
        sensor = {'id': 0, 'name': 'Tutti i sensori', 'icon': 'fas fa-search', 'unit': ''}
        predictions = Prediction.objects
        data_month = []
        measures = None
    else:
        sensor = Sensor.objects.get(pk=sensor_id)
        predictions = sensor.prediction_set
        data_month = []
        history = sensor.dailydata_set.filter(date__gte='2019-07-17').order_by('date')
        measures = sensor.get_measures()
        all_data = history.values('date', *measures)

        for key, group_iter in groupby(all_data, key=lambda x: x['date'].strftime('%Y-%m')):
            group = list(group_iter)
            data_month.append({'date': key,
                               'tot': np.mean([e['tot'] for e in group]) if 'tot' in measures else None,
                               'avg': np.mean([e['avg'] for e in group]) if 'avg' in measures else None,
                               'max': np.max([e['max'] for e in group]) if 'max' in measures else None,
                               'min': np.min([e['min'] for e in group]) if 'min' in measures else None})
        sensor = sensor.to_js()
    predictions = predictions.filter(date__gte='2019-07-17').order_by('date')

    if not predictions:
        return {
            'lastUpdate': get_last_update('prediction'),
            'sensor': sensor,
            'error': 'No data'
        }

    anomalies_all = predictions.filter(anomaly=True).values('date', 'sensor__name', 'measure', 'method',
                                                            'actual', 'prediction')
    anomalies_aggr = []
    for key, group_iter in sort_and_group(anomalies_all, key=lambda x: (x['date'], x['sensor__name'], x['measure'])):
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
    anomalies_month = []
    for key, group_iter in groupby(anomalies_date, key=lambda x: x['date'].strftime('%Y-%m')):
        group = list(group_iter)
        anomalies_month.append({'date': key,
                                'minor': sum(len(g['minor']) for g in group),
                                'medium': sum(len(g['medium']) for g in group),
                                'major': sum(len(g['major']) for g in group)})

    anomalies_year = []
    for key, group_iter in groupby(anomalies_date, key=lambda x: x['date'].strftime('%Y')):
        group = list(group_iter)
        anomalies_year.append({'date': key,
                               'minor': sum(len(g['minor']) for g in group),
                               'medium': sum(len(g['medium']) for g in group),
                               'major': sum(len(g['major']) for g in group)})

    anomalies_measures = []
    anomalies_measures_year = []
    if measures:
        anomalies_measures_list = [key for key, group_iter in
                                   sort_and_group(anomalies_all, key=lambda x: (x['date'], x['measure']))]
        for key, group_iter in groupby(anomalies_measures_list, key=lambda x: x[0].strftime('%Y-%m')):
            group = list(group_iter)
            anomaly_measures = {'date': key}
            for m in measures:
                anomaly_measures[m] = sum(g[1] == m for g in group)
            anomalies_measures.append(anomaly_measures)

        for key, group_iter in groupby(anomalies_measures_list, key=lambda x: x[0].strftime('%Y')):
            group = list(group_iter)
            anomaly_measures = {'date': key}
            for m in measures:
                anomaly_measures[m] = sum(g[1] == m for g in group)
            anomalies_measures_year.append(anomaly_measures)

    return {
        'lastUpdate': get_last_update('prediction'),
        'sensor': sensor,
        'measures': measures,
        'allAnomalies': anomalies_date,
        'anomaliesMonth': anomalies_month,
        'dataMonth': data_month,
        'anomaliesYear': anomalies_year,
        'anomaliesMeasures': anomalies_measures,
        'anomaliesMeasuresYear': anomalies_measures_year
    }
