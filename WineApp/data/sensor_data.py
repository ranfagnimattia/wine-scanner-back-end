from datetime import timedelta
from itertools import chain, groupby

import numpy as np

from WineApp.data.update_data import get_last_update
from WineApp.models import Sensor


def get_series(sensor: Sensor, measure: str):
    train_set = sensor.dailydata_set.filter(date__lt=sensor.startTestSet).order_by('date')
    test_set = sensor.dailydata_set.filter(date__gte=sensor.startTestSet).order_by('date')

    date = list(test_set.values_list('date', flat=True))
    test_set = list(test_set.values_list(measure, flat=True))
    train_set = list(train_set.values_list(measure, flat=True))
    return test_set, train_set, date


def get_daily_data(sensor_id: int = 1) -> dict:
    sensor = Sensor.objects.get(pk=sensor_id)
    history = sensor.dailydata_set.filter(date__gte='2019-07-17').order_by('date')
    measures = sensor.get_measures()

    all_data = history.values('date', *measures)
    last_month = list(_get_date_interval(all_data, all_data.last()['date'], 30))
    tot = np.mean([e['tot'] for e in last_month]) if 'tot' in measures else np.NaN
    avg = np.mean([e['avg'] for e in last_month]) if 'avg' in measures else np.NaN
    avg_min = np.mean([e['min'] for e in last_month]) if 'min' in measures else np.NaN
    avg_max = np.mean([e['max'] for e in last_month]) if 'max' in measures else np.NaN
    diff = _difference(last_month, avg, avg_min, avg_max, tot)

    last_month_stats = {k: v for k, v in {
        'tot': tot,
        'avg': avg,
        'max': np.max([e['max'] if 'max' in e else np.NaN for e in last_month]),
        'min': np.min([e['min'] if 'min' in e else np.NaN for e in last_month])
    }.items() if not np.isnan(v)}

    last = all_data.last()
    week_avg = np.mean([e[measures[0]] for e in list(_get_date_interval(all_data, all_data.last()['date'], 7))])
    trend = {
        'day': last[measures[0]] - all_data.reverse()[1][measures[0]],
        'week': last[measures[0]] - week_avg,
        'month': last[measures[0]] - last_month_stats[measures[0]]
    }

    for elem in chain(all_data, last_month):
        elem['date'] = elem['date'].strftime('%Y-%m-%d')

    return {
        'lastUpdate': get_last_update('daily'),
        'sensor': sensor.to_js(),
        'measures': measures,
        'chartAll': [list(elem.values()) for elem in all_data],
        'chartLastMonth': last_month,
        'chartDiff': diff,
        'last': all_data.last(),
        'lastMonthStats': last_month_stats,
        'trend': trend
    }


def get_realtime_data(sensor_id: int = 1) -> dict:
    sensor = Sensor.objects.get(pk=sensor_id)
    all_data = sensor.realtimedata_set.order_by('time').values('time', 'value')
    # Data
    last_value = all_data.last()['value']
    last_time = all_data.last()['time']
    last24h = _get_interval(all_data, last_time, 1, True)

    # previous24h = _get_interval(all_data, last_time, 2, True)
    previous_week = all_data.filter(time__gte=last_time - timedelta(days=8), time__lte=last_time - timedelta(days=1))

    # Cards
    last_day_values = _get_interval(all_data, last_time.date(), 0, True).order_by('value')
    last_day_stats = {
        'avg': np.mean([e['value'] for e in last_day_values]),
        'max': last_day_values.last()['value'],
        'min': last_day_values.first()['value'],
        'maxTime': last_day_values.last()['time'].strftime('%H:%M:%S'),
        'minTime': last_day_values.first()['time'].strftime('%H:%M:%S')
    }
    if sensor.tot:
        last_day_stats['tot'] = np.sum([e['value'] for e in last_day_values])

    trend = {
        'previous': last_value - all_data.reverse()[1]['value'],
        'lastDay': last_value - last_day_stats['avg']
    }

    # Charts
    last24h_aggr = [[key, np.mean([e['value'] for e in group])] for key, group in
                    groupby(last24h, key=lambda x: x['time'].strftime('%Y-%m-%d %H'))]

    previous_week_aggr = [[key, np.mean([e['value'] for e in group])] for key, group in
                          groupby(previous_week, key=lambda x: x['time'].strftime('%H'))]

    chart_diff = {
        'avg': [[last[0], prev[1]] for last, prev in zip(last24h_aggr, previous_week_aggr)],
        'diff': [[last[0], last[1] - prev[1]] for last, prev in zip(last24h_aggr, previous_week_aggr)]
    }

    for elem in chain(all_data, last24h):
        elem['time'] = elem['time'].strftime('%Y-%m-%d %H:%M:%S')

    return {
        'lastUpdate': get_last_update('realtime'),
        'sensor': sensor.to_js(),
        'mainMeasure': 'tot' if sensor.tot else 'avg',
        'chartAll': [list(elem.values()) for elem in all_data],
        'chartLast24h': [list(elem.values()) for elem in last24h],
        'chartDiff': chart_diff,
        'last': last_value,
        'lastTime': last_time.strftime('%H:%M:%S'),
        'lastDayStats': last_day_stats,
        'trend': trend
    }


# Private
def _get_interval(values, date, look_back, flag=False):
    start = date - timedelta(days=look_back)
    if not flag:
        val = values.filter(date__gte=start)
    else:
        end = date + timedelta(days=1 - look_back)
        val = values.filter(time__gte=start, time__lte=end)
    return val


def _get_date_interval(values, date, start, end=0):
    return values.filter(date__gt=date - timedelta(days=start), date__lte=date - timedelta(days=end))


def _difference(values, avg, minimum, maximum, tot):
    diff = []
    for e in values:
        diff.append({'date': e['date'].strftime('%Y-%m-%d')})
        if not np.isnan(avg):
            diff[-1]['avg'] = e['avg'] - avg
        if not np.isnan(tot):
            diff[-1]['tot'] = e['tot'] - tot
        if not np.isnan(minimum):
            diff[-1]['min'] = e['min'] - minimum
        if not np.isnan(maximum):
            diff[-1]['max'] = e['max'] - maximum
    return diff
