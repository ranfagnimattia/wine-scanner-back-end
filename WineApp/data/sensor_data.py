from datetime import datetime, timedelta
from xml.etree import ElementTree

import numpy as np
import requests
from django.http import Http404

from WineApp.models import DailyData, Sensor, RealTimeData


def update_daily_data():
    try:
        start_date = DailyData.objects.latest('date').date
        start_date = datetime.combine(start_date, datetime.min.time())
    except DailyData.DoesNotExist:
        start_date = datetime(2019, 7, 17)
    if start_date < datetime(2019, 7, 17):
        start_date = datetime(2019, 7, 17)
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    parameter = {'username': 'collosorbo', 'password': '10sorbo19', 'start_date': start_date,
                 'end_date': end_date, 'day_average': '1'}
    response = requests.post('https://live.netsens.it/export/xml_export_1A.php', data=parameter)

    if response.status_code != requests.codes.ok:
        return 'Request error'
    root_elem = ElementTree.fromstring(response.content)
    if root_elem.get('errore') != '0':
        return 'API error: ' + root_elem.get('messaggio')
    station_elem = root_elem[0]

    last_day = DailyData.objects.filter(date__gte=start_date)
    n_updated = last_day.count()
    last_day.delete()
    debug_data = []
    new_data = []
    n_created = 0
    for unit_elem in station_elem.findall('unita'):
        for date_elem in unit_elem.findall('giorno'):
            string = ''
            for sensor_elem in date_elem.findall('sensore'):
                try:
                    sensor = Sensor.objects.get(name=sensor_elem.get('nome'))
                    # data, created = DailyData.objects.get_or_create(date=date_elem.get('data'), sensor=sensor)
                    data = DailyData(date=date_elem.get('data'), sensor=sensor)
                    if sensor.values:
                        data.avg = sensor_elem.get('media')
                        data.max = sensor_elem.get('massima')
                        data.maxTime = sensor_elem.get('ora_massima')
                        data.min = sensor_elem.get('minima')
                        data.minTime = sensor_elem.get('ora_minima')
                        if sensor.name == 'Pressione atmosferica':
                            data.avg = round(float(data.avg) / 10, 3)
                            data.max = round(float(data.max) / 10, 3)
                            data.min = round(float(data.min) / 10, 3)
                    if sensor.tot:
                        data.tot = sensor_elem.get('cumulato')
                    # data.save()
                    new_data.append(data)
                    # string += sensor_elem.get('nome') + str(created) + ' '
                    n_created += 1
                except Sensor.DoesNotExist:
                    # string += sensor_elem.get('nome') + 'NONE '
                    pass

            # debug_data.append(date_elem.get('data') + '  ' + string)

    DailyData.objects.bulk_create(new_data)
    debug_data.append(start_date + '   ' + end_date)
    debug_data.append('Updated: ' + str(n_updated) + ', Created: ' + str(n_created - n_updated))
    return {'updated': n_updated, 'created': n_created - n_updated}


def update_realtime_data():
    try:
        start_date = RealTimeData.objects.latest('time').time
    except RealTimeData.DoesNotExist:
        start_date = datetime(2019, 7, 17)
    end_date = datetime.now()

    debug_data = []
    new_data = []
    n_created = 0
    while start_date < end_date:
        start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        start_date += timedelta(days=6)
        end_str = start_date.strftime('%Y-%m-%d %H:%M:%S')

        parameter = {'username': 'collosorbo', 'password': '10sorbo19', 'start_date': start_str,
                     'end_date': end_str}
        response = requests.post('https://live.netsens.it/export/xml_export_1A.php', data=parameter)

        if response.status_code != requests.codes.ok:
            return 'Request error'
        root_elem = ElementTree.fromstring(response.content)
        if root_elem.get('errore') != '0':
            return 'API error: ' + root_elem.get('messaggio')
        station_elem = root_elem[0]

        for unit_elem in station_elem.findall('unita'):
            for sensor_elem in unit_elem.findall('sensore'):
                try:
                    sensor = Sensor.objects.get(name=sensor_elem.get('nome'))
                    for measure_elem in sensor_elem.findall('misura'):
                        if not RealTimeData.objects.filter(time=measure_elem.get('data_ora'),
                                                           sensor=sensor).exists():
                            new_data.append(RealTimeData(time=measure_elem.get('data_ora'),
                                                         sensor=sensor, value=measure_elem.get('valore')))
                            n_created += 1
                except Sensor.DoesNotExist:
                    debug_data.append(sensor_elem.get('nome') + '  NONE')
                    pass

        debug_data.append(start_str + '   ' + end_str)
        debug_data.append('Created: ' + str(n_created))
    RealTimeData.objects.bulk_create(new_data)
    return debug_data


def get_daily_data(sensor_id: int = 1) -> (list, Sensor, list):
    """
    Get daily data of a sensor

    :param sensor_id: int
    :return: list of lists [date, avg, min, max] or [date,tot], sensor object
    """
    sensor = Sensor.objects.get(pk=sensor_id)
    history = sensor.dailydata_set.filter(date__gte='2019-07-17').order_by('date')
    if sensor.tot and sensor.values:
        values = history.values('date', 'tot', 'avg', 'min', 'max')
        val = list(values)
        avg = np.mean([e['avg'] for e in (val[-31:])])
        min = np.mean([e['min'] for e in (val[-31:])])
        max = np.mean([e['max'] for e in (val[-31:])])
        tot = np.mean([e['tot'] for e in (val[-31:])])
    elif sensor.tot:
        values = history.values('date', 'tot')
        val = list(values)
        avg = np.NaN
        min = np.NaN
        max = np.NaN
        tot = np.mean([e['tot'] for e in (val[-31:])])
    else:
        values = history.values('date', 'avg', 'min', 'max')
        val = list(values)
        avg = np.mean([e['avg'] for e in (val[-31:])])
        min = np.mean([e['min'] for e in (val[-31:])])
        max = np.mean([e['max'] for e in (val[-31:])])
        tot = np.NaN
    if sensor.tot:
        week_avg = {'tot': np.mean([e['tot'] for e in (val[-7:])])}
    else:
        week_avg = {'avg': np.mean([e['avg'] for e in (val[-7:])])}
    print(avg, min, max, tot)
    diff = _difference(val[-31:], avg, min, max, tot)
    print(diff)
    lastMonthMean = {'avg': avg, 'min': min, 'max': max, 'tot': tot}
    lastMonthMean = {k: round(v, 2) for k, v in lastMonthMean.items() if not np.isnan(v)}
    print(lastMonthMean)
    for elem in values:
        elem['date'] = elem['date'].strftime('%Y-%m-%d')

    values_list = [list(elem.values()) for elem in values]
    return values_list, sensor, list(values), diff, lastMonthMean, week_avg


def _difference(values, avg, min, max, tot):
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
