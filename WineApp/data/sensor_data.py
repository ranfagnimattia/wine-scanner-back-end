from datetime import datetime, timedelta
from xml.etree import ElementTree

import requests
from django.http import Http404

from WineApp.models import DailyData, Sensor, RealTimeData


def update_daily_data():
    try:
        start_date = DailyData.objects.latest('date').date.strftime('%Y-%m-%d')
    except DailyData.DoesNotExist:
        start_date = '2019-07-17'
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

    debug_data = []
    n_updated = 0
    n_created = 0
    for unit_elem in station_elem.findall('unita'):
        for date_elem in unit_elem.findall('giorno'):
            string = ''
            for sensor_elem in date_elem.findall('sensore'):
                try:
                    sensor = Sensor.objects.get(name=sensor_elem.get('nome'))
                    data, created = DailyData.objects.get_or_create(date=date_elem.get('data'), sensor=sensor)
                    if sensor.values:
                        data.avg = sensor_elem.get('media')
                        data.max = sensor_elem.get('massima')
                        data.maxTime = sensor_elem.get('ora_massima')
                        data.min = sensor_elem.get('minima')
                        data.minTime = sensor_elem.get('ora_minima')
                    if sensor.tot:
                        data.tot = sensor_elem.get('cumulato')
                    data.save()
                    string += sensor_elem.get('nome') + str(created) + ' '
                    if created:
                        n_created += 1
                    else:
                        n_updated += 1
                except Sensor.DoesNotExist:
                    string += sensor_elem.get('nome') + 'NONE '
                    pass

            debug_data.append(date_elem.get('data') + '  ' + string)

    debug_data.append(start_date + '   ' + end_date)
    debug_data.append('Updated: ' + str(n_updated) + ', Created: ' + str(n_created))
    return debug_data


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
    history = sensor.dailydata_set.order_by('date')
    if sensor.tot:
        values = history.values('date', 'tot')
    else:
        values = history.values('date', 'avg', 'min', 'max')
    for elem in values:
        elem['date'] = elem['date'].strftime('%Y-%m-%d')
    values_list = [list(elem.values()) for elem in values]
    return values_list, sensor, list(values)


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
