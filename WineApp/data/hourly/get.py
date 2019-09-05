from collections import deque
from datetime import timedelta
from itertools import chain, groupby

import numpy as np

from WineApp.data.utils import get_last_update, get_time_interval, sort_and_group, str_to_class
from WineApp.models import Sensor


def get_data(sensor_id: int = 1) -> dict:
    sensor = Sensor.objects.get(pk=sensor_id)
    all_data = str_to_class('Hourly' + sensor.table).objects.all().order_by('time').values('time', 'value')
    # Data
    last_value = all_data.last()['value']
    last_time = all_data.last()['time']
    last24h = get_time_interval(all_data, last_time, 1)

    # previous24h = _get_interval(all_data, last_time, 2, True)
    previous_week = all_data.filter(time__gte=last_time - timedelta(days=8), time__lte=last_time - timedelta(days=1))

    # Cards
    last_day_values = get_time_interval(all_data, last_time.date(), 0).order_by('value')
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
    last24h_aggr = [[key[0], key[1], np.mean([e['value'] for e in group])] for key, group in
                    groupby(last24h, key=lambda x: (x['time'].strftime('%Y-%m-%d'), x['time'].strftime('%H')))]

    previous_week_aggr = [[key, np.mean([e['value'] for e in group])] for key, group in
                          sort_and_group(previous_week, key=lambda x: x['time'].strftime('%H'))]

    week_aggr_ordered = deque(previous_week_aggr)
    week_aggr_ordered.rotate(24 - int(last24h_aggr[0][1]))
    chart_diff = {
        'avg': [[last[0] + ' ' + last[1], prev[1]] for last, prev in zip(last24h_aggr, week_aggr_ordered)],
        'diff': [[last[0] + ' ' + last[1], last[2] - prev[1]] for last, prev in zip(last24h_aggr, week_aggr_ordered)]
    }

    for elem in chain(all_data, last24h):
        elem['time'] = elem['time'].strftime('%Y-%m-%d %H:%M:%S')

    return {
        'lastUpdate': get_last_update('hourly'),
        'sensor': sensor.to_js(),
        'mainMeasure': 'tot' if sensor.tot else 'avg',
        'allData': [list(elem.values()) for elem in all_data],
        'last24h': [list(elem.values()) for elem in last24h],
        'diff': chart_diff,
        'last': last_value,
        'lastTime': last_time.strftime('%H:%M:%S'),
        'lastDayStats': last_day_stats,
        'trend': trend,
        'lastWeekTime': (last_time - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    }
