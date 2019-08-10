from datetime import timedelta, datetime

import numpy as np
from django.http import Http404

from WineApp.models import DailyData, Sensor


def get_daily_data(sensor_id: int = 1) -> (list, Sensor, list):
    """
    Get daily data of a sensor

    :param sensor_id: int
    :return: list of lists [date, avg, min, max] or [date,tot], sensor object
    """
    sensor = Sensor.objects.get(pk=sensor_id)
    history = sensor.dailydata_set.filter(date__gte='2019-07-17').order_by('date')

    if sensor.tot and sensor.values:
        all_data = history.values('date', 'tot', 'avg', 'max', 'min')
        val = list(_get_interval(all_data, all_data.last()['date'], 31))
        avg = np.mean([e['avg'] for e in val])
        min = np.mean([e['min'] for e in val])
        max = np.mean([e['max'] for e in val])
        tot = np.mean([e['tot'] for e in val])
        week_avg = {'tot': np.mean([e['tot'] for e in list(_get_interval(all_data, all_data.last()['date'], 7))])}
        categories = ['Tot', 'Avg', 'Max', 'Min']
    elif sensor.tot:
        all_data = history.values('date', 'tot')
        val = list(_get_interval(all_data, all_data.last()['date'], 31))
        avg = np.NaN
        min = np.NaN
        max = np.NaN
        tot = np.mean([e['tot'] for e in val])
        week_avg = {'tot': np.mean([e['tot'] for e in list(_get_interval(all_data, all_data.last()['date'], 7))])}
        categories = ['Tot']
    else:
        all_data = history.values('date', 'avg', 'max', 'min')
        val = list(_get_interval(all_data, all_data.last()['date'], 31))
        avg = np.mean([e['avg'] for e in val])
        min = np.mean([e['min'] for e in val])
        max = np.mean([e['max'] for e in val])
        tot = np.NaN
        week_avg = {'avg': np.mean([e['avg'] for e in list(_get_interval(all_data, all_data.last()['date'], 7))])}
        categories = ['Avg', 'Max', 'Min']
    diff = _difference(val, avg, min, max, tot, np.NaN)
    last_month_stats = {'avg': avg, 'min': min, 'max': max, 'tot': tot}
    last_month_stats = {k: round(v, 2) for k, v in last_month_stats.items() if not np.isnan(v)}

    for elem in all_data:
        elem['date'] = elem['date'].strftime('%Y-%m-%d')

    all_data_list = [list(elem.values()) for elem in all_data]

    return all_data_list, categories, sensor, list(all_data), diff, last_month_stats, week_avg


def get_real_time_data(sensor_id: int = 1):
    sensor = Sensor.objects.get(pk=sensor_id)
    history = sensor.realtimedata_set.order_by('time')
    all_data = history.values('time', 'value')

    today = datetime.today()

    last24h = _get_interval(all_data, today, 1, True)
    for elem in last24h:
        elem['time'] = elem['time'].strftime('%Y-%m-%d %H:%M:%S')
    avg24h = np.mean([e['value'] for e in last24h])

    today = today.date()

    today_values = _get_interval(all_data, today, 0, True)
    ordered = today_values.order_by('value')
    today_stats = {'min_time': ordered.first()['time'].strftime('%H:%M:%S'), 'min_value': ordered.first()['value'],
                  'max_time': ordered.last()['time'].strftime('%H:%M:%S'),
                  'max_value': ordered.last()['value']}

    for elem in today_values:
        elem['time'] = elem['time'].strftime('%Y-%m-%d %H:%M:%S')
    today_avg = np.mean([e['value'] for e in today_values])

    yesterday_values = _get_interval(all_data, today, 1, True)
    for elem in yesterday_values:
        elem['time'] = elem['time'].strftime('%Y-%m-%d %H:%M:%S')
    yesterday_avg = np.mean([e['value'] for e in yesterday_values])

    # Per il grafico a colonne
    diff = _difference(last24h, np.NaN, np.NaN, np.NaN, np.NaN, avg24h)

    # Per il grafico finale
    for elem in all_data:
        elem['time'] = elem['time'].strftime('%Y-%m-%d %H:%M:%S')
    all_data_list = [list(elem.values()) for elem in all_data]

    return all_data_list, diff, yesterday_avg, today_avg, last24h, today_stats


def _get_interval(values, date, lookback, flag=False):
    start = date - timedelta(days=lookback)
    if not flag:
        val = values.filter(date__gte=start)
    else:
        end = date + timedelta(days=1 - lookback)
        val = values.filter(time__gte=start, time__lte=end)
    return val


def _difference(values, avg, min, max, tot, val):
    diff = []
    for e in values:
        if not np.isnan(val):
            diff.append({'date': e['time']})
            diff[-1]['value'] = e['value'] - val
        else:
            diff.append({'date': e['date'].strftime('%Y-%m-%d')})
            if not np.isnan(avg):
                diff[-1]['avg'] = e['avg'] - avg
            if not np.isnan(tot):
                diff[-1]['tot'] = e['tot'] - tot
            if not np.isnan(min):
                diff[-1]['min'] = e['min'] - min
            if not np.isnan(max):
                diff[-1]['max'] = e['max'] - max
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
