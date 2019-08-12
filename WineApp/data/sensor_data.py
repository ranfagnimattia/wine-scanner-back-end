from datetime import timedelta, datetime

import numpy as np
from django.http import Http404
from django.urls import reverse

from WineApp.models import DailyData, Sensor


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
        categories = ['Tot', 'Avg', 'Max', 'Min']
    elif sensor.tot:
        all_data = history.values('date', 'tot')
        val = list(_get_interval(all_data, all_data.last()['date'], 31))
        avg = np.NaN
        avg_min = np.NaN
        avg_max = np.NaN
        tot = np.mean([e['tot'] for e in val])
        week_avg = {'tot': np.mean([e['tot'] for e in list(_get_interval(all_data, all_data.last()['date'], 7))])}
        categories = ['Tot']
    else:
        all_data = history.values('date', 'avg', 'max', 'min')
        val = list(_get_interval(all_data, all_data.last()['date'], 31))
        avg = np.mean([e['avg'] for e in val])
        avg_min = np.mean([e['min'] for e in val])
        avg_max = np.mean([e['max'] for e in val])
        tot = np.NaN
        week_avg = {'avg': np.mean([e['avg'] for e in list(_get_interval(all_data, all_data.last()['date'], 7))])}
        categories = ['Avg', 'Max', 'Min']
    diff = _difference(val, avg, avg_min, avg_max, tot, np.NaN)
    last_month_stats = {'avg': avg, 'min': np.min([e['min'] if 'min' in e else np.NaN for e in val]),
                        'max': np.max([e['max'] if 'max' in e else np.NaN for e in val]),
                        'tot': tot}
    last_month_stats = {k: round(v, 2) for k, v in last_month_stats.items() if not np.isnan(v)}

    for elem in all_data:
        elem['date'] = elem['date'].strftime('%Y-%m-%d')

    all_data_list = [list(elem.values()) for elem in all_data]

    # return all_data_list, categories, sensor, list(all_data), diff, last_month_stats, week_avg
    return {
        'getUrl': reverse('WineApp:ajax.getDailyData'),
        'updateUrl': reverse('WineApp:ajax.updateDailyData'),
        'allData': all_data_list,
        'categories': categories,
        'last': list(all_data)[-1],
        'lastMonth': list(all_data)[-31:],
        'diff': diff,
        'monthMean': last_month_stats,
        'weekMean': week_avg,
        'yesterday': list(all_data)[-2],
        'sensor': {'tot': sensor.tot, 'values': sensor.values, 'id': sensor.id, 'name': sensor.name,
                   'unit': sensor.unit, 'icon': sensor.icon}
    }


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


def _difference(values, avg, minimum, maximum, tot, val):
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
