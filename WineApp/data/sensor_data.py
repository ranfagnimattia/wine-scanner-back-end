from datetime import timedelta, datetime
from itertools import chain, groupby

import numpy as np

from WineApp.models import Sensor, LastUpdate


def get_daily_data(sensor_id: int = 1) -> dict:
    """
    Get daily data of a sensor

    :param sensor_id: int
    :return: object with parameter for js
    """
    sensor = Sensor.objects.get(pk=sensor_id)
    history = sensor.dailydata_set.filter(date__gte='2019-07-17').order_by('date')

    if sensor.tot and sensor.values:
        all_data = history.values('date', 'tot', 'avg', 'max', 'min')
        val = list(_get_interval(all_data, all_data.last()['date'], 31))
        avg = np.mean([e['avg'] for e in val])
        avg_min = np.mean([e['min'] for e in val])
        avg_max = np.mean([e['max'] for e in val])
        tot = np.mean([e['tot'] for e in val])
        week_avg = {'tot': np.mean([e['tot'] for e in list(_get_interval(all_data, all_data.last()['date'], 7))])}
        measures = ['Tot', 'Avg', 'Max', 'Min']
    elif sensor.tot:
        all_data = history.values('date', 'tot')
        val = list(_get_interval(all_data, all_data.last()['date'], 31))
        avg = np.NaN
        avg_min = np.NaN
        avg_max = np.NaN
        tot = np.mean([e['tot'] for e in val])
        week_avg = {'tot': np.mean([e['tot'] for e in list(_get_interval(all_data, all_data.last()['date'], 7))])}
        measures = ['Tot']
    else:
        all_data = history.values('date', 'avg', 'max', 'min')
        val = list(_get_interval(all_data, all_data.last()['date'], 31))
        avg = np.mean([e['avg'] for e in val])
        avg_min = np.mean([e['min'] for e in val])
        avg_max = np.mean([e['max'] for e in val])
        tot = np.NaN
        week_avg = {'avg': np.mean([e['avg'] for e in list(_get_interval(all_data, all_data.last()['date'], 7))])}
        measures = ['Avg', 'Max', 'Min']
    diff = _difference(val, avg, avg_min, avg_max, tot)
    last_month_stats = {'avg': avg, 'min': np.min([e['min'] if 'min' in e else np.NaN for e in val]),
                        'max': np.max([e['max'] if 'max' in e else np.NaN for e in val]),
                        'tot': tot}
    last_month_stats = {k: round(v, 2) for k, v in last_month_stats.items() if not np.isnan(v)}

    for elem in all_data:
        elem['date'] = elem['date'].strftime('%Y-%m-%d')

    all_data_list = [list(elem.values()) for elem in all_data]

    # return all_data_list, categories, sensor, list(all_data), diff, last_month_stats, week_avg
    return {
        'lastUpdate': _get_last_update('daily'),
        'allData': all_data_list,
        'measures': measures,
        'last': list(all_data)[-1],
        'lastMonth': list(all_data)[-31:],
        'diff': diff,
        'monthMean': last_month_stats,
        'weekMean': week_avg,
        'yesterday': list(all_data)[-2],
        'sensor': sensor.to_js()
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
        'sensor': sensor.to_js(),
        'lastUpdate': _get_last_update('realtime'),
        'chartAll': [list(elem.values()) for elem in all_data],
        'chartLast24h': [list(elem.values()) for elem in last24h],
        'chartDiff': chart_diff,
        'mainMeasure': 'tot' if sensor.tot else 'avg',
        'last': last_value,
        'lastTime': last_time.strftime('%H:%M:%S'),
        'lastDayStats': last_day_stats,
        'trend': trend
    }


def _get_last_update(update_type):
    try:
        last_datetime = LastUpdate.objects.get(type=update_type).time
        return {'date': _relative_date(last_datetime), 'time': last_datetime.strftime('%H:%M')}
    except LastUpdate.DoesNotExist:
        return {'date': '', 'time': ''}


def _relative_date(date: datetime):
    diff = datetime.today() - date
    if diff.days == 0:
        return 'oggi'
    elif diff.days == 1:
        return 'ieri'
    elif diff.days <= 10:
        return '{} giorni fa'.format(diff.days)
    elif diff.days <= 300:
        return 'il ' + date.strftime('%d/%m')
    else:
        return 'il ' + date.strftime('%d/%m/%Y')


def _get_interval(values, date, look_back, flag=False):
    start = date - timedelta(days=look_back)
    if not flag:
        val = values.filter(date__gte=start)
    else:
        end = date + timedelta(days=1 - look_back)
        val = values.filter(time__gte=start, time__lte=end)
    return val


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


def get_series(sensor, measure: str):
    train_set = sensor.dailydata_set.filter(date__lt=sensor.startTestSet).order_by('date')
    test_set = sensor.dailydata_set.filter(date__gte=sensor.startTestSet).order_by('date')

    date = list(test_set.values_list('date', flat=True))
    test_set = list(test_set.values_list(measure, flat=True))
    train_set = list(train_set.values_list(measure, flat=True))

    return test_set, train_set, date
    # fields = {'airTemperature': 'Temperatura aria', 'rain': 'Pioggia', 'windSpeed': 'Velocità vento',
    #           'dewPoint': 'Punto di rugiada'}
    # if field not in fields.keys():
    #     raise Http404("Field does not exist")
    # sensor = Sensor.objects.get(name=fields[field])
    # train_set = DailyData.objects.filter(sensor=sensor, date__lte='2018-12-31').order_by('date')
    # train_list = list(train_set.values_list(measure, flat=True))
    # test_set = DailyData.objects.filter(sensor=sensor, date__gte='2019-01-01').order_by('date')
    # test_list = list(test_set.values_list(measure, flat=True))
    # return train_list, test_list, field in fields.keys(), test_set.values_list('date', flat=True)
