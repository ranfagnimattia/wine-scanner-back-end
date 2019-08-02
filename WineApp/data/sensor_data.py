from xml.etree import ElementTree

import requests
from django.utils import timezone

from WineApp.models import DailyData, Sensor


def update_daily_data():
    try:
        start_date = DailyData.objects.latest('date').date.strftime('%Y-%m-%d')
    except DailyData.DoesNotExist:
        start_date = '2019-07-17'
    end_date = timezone.localtime().strftime('%Y-%m-%d')
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
                except Sensor.DoesNotExist:
                    string += sensor_elem.get('nome') + 'NONE '
                    pass

            debug_data.append(date_elem.get('data') + '  ' + string)

    debug_data.append(start_date + '   ' + end_date)
    return debug_data
