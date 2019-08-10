from datetime import timedelta
from xml.etree import ElementTree

import numpy as np
from django.http import Http404

from WineApp.models import DailyData, Sensor, RealTimeData


def get_daily_data(sensor_id: int = 1) -> (list, Sensor, list):
    """
    Get daily data of a sensor

    :param sensor_id: int
    :return: list of lists [date, avg, min, max] or [date,tot], sensor object
    """
    sensor = Sensor.objects.get(pk=sensor_id)
    history = sensor.dailydata_set.filter(date__gte='2019-07-17').order_by('date')

    if sensor.tot and sensor.values:
        values = history.values('date', 'tot', 'avg', 'max', 'min')
        val = list(_get_interval(values, values.last()['date'], 31))
        avg = np.mean([e['avg'] for e in val])
        min = np.mean([e['min'] for e in val])
        max = np.mean([e['max'] for e in val])
        tot = np.mean([e['tot'] for e in val])
        scheme = [
            {
                "name": "Time",
                "type": "date",
                "format": "%Y-%m-%d"
            },
            {
                "name": "Tot",
                "type": "number"
            },
            {
                "name": "Avg",
                "type": "number"
            },
            {
                "name": "Max",
                "type": "number"
            },
            {
                "name": "Min",
                "type": "number"
            }]
    elif sensor.tot:
        values = history.values('date', 'tot')
        val = list(_get_interval(values, values.last()['date'], 31))
        avg = np.NaN
        min = np.NaN
        max = np.NaN
        tot = np.mean([e['tot'] for e in val])
        scheme = [
            {
                "name": "Time",
                "type": "date",
                "format": "%Y-%m-%d"
            },
            {
                "name": "Tot",
                "type": "number"
            }]
    else:
        values = history.values('date', 'avg', 'max', 'min')
        val = list(_get_interval(values, values.last()['date'], 31))
        avg = np.mean([e['avg'] for e in val])
        min = np.mean([e['min'] for e in val])
        max = np.mean([e['max'] for e in val])
        tot = np.NaN
        scheme = [
            {
                "name": "Time",
                "type": "date",
                "format": "%Y-%m-%d"
            },
            {
                "name": "Avg",
                "type": "number"
            },
            {
                "name": "Max",
                "type": "number"
            },
            {
                "name": "Min",
                "type": "number"
            }]
    if sensor.tot:
        week_avg = {'tot': np.mean([e['tot'] for e in list(_get_interval(values, values.last()['date'], 7))])}
    else:
        week_avg = {'avg': np.mean([e['avg'] for e in list(_get_interval(values, values.last()['date'], 7))])}

    diff = _difference(val, avg, min, max, tot, np.NaN)
    last_month_mean = {'avg': avg, 'min': min, 'max': max, 'tot': tot}
    last_month_mean = {k: round(v, 2) for k, v in last_month_mean.items() if not np.isnan(v)}

    for elem in values:
        elem['date'] = elem['date'].strftime('%Y-%m-%d')

    values_list = [list(elem.values()) for elem in values]

    return values_list, scheme, sensor, list(values), diff, last_month_mean, week_avg


def _get_interval(values, date, param):
    start = date - timedelta(days=param)
    val = values.filter(date__gte=start)
    return val


def _difference(values, avg, min, max, tot, val):
    diff = []
    for e in values:
        diff.append({'date': e['date'].strftime('%Y-%m-%d')})
        if not np.isnan(avg):
            diff[-1]['avg'] = e['avg'] - avg
        if not np.isnan(tot):
            diff[-1]['tot'] = e['tot'] - tot
        if not np.isnan(min):
            diff[-1]['min'] = e['min'] - min
        if not np.isnan(max):
            diff[-1]['max'] = e['max'] - max
        if not np.isnan(val):
            diff[-1]['values'] = e['value'] - val
    return diff


# todo choose size of train and test set
def get_series(field: str, measure: str):
    fields = {'airTemperature': 'Temperatura aria', 'rain': 'Pioggia', 'windSpeed': 'Velocità vento',
              'dewPoint': 'Punto di rugiada'}
    if field not in fields.keys():
        raise Http404("Field does not exist")
    sensor = Sensor.objects.get(name=fields[field])
    train_set = DailyData.objects.filter(sensor=sensor, date__lte='2018-12-31').order_by('date')
    train_list = list(train_set.values_list(measure, flat=True))
    test_set = DailyData.objects.filter(sensor=sensor, date__gte='2019-01-01').order_by('date')
    test_list = list(test_set.values_list(measure, flat=True))
    return train_list, test_list, field in fields.keys(), test_set.values_list('date', flat=True)
