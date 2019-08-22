from itertools import chain

import numpy as np

from WineApp.data.utils import get_last_update, get_date_interval
from WineApp.models import Sensor


def get_data(sensor_id: int = 1) -> dict:
    sensor = Sensor.objects.get(pk=sensor_id)
    history = sensor.dailydata_set.filter(date__gte='2019-07-17').order_by('date')
    measures = sensor.get_measures()

    all_data = history.values('date', *measures)
    last_month = list(get_date_interval(all_data, all_data.last()['date'], 30))
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
    week_avg = np.mean([e[measures[0]] for e in list(get_date_interval(all_data, all_data.last()['date'], 7))])
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
        'allData': [list(elem.values()) for elem in all_data],
        'lastMonth': last_month,
        'diff': diff,
        'last': all_data.last(),
        'lastMonthStats': last_month_stats,
        'trend': trend
    }


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
