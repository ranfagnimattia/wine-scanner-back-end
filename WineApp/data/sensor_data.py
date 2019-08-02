from xml.etree import ElementTree

import requests
from django.utils import timezone

from WineApp.models import DailyData, Sensor


def update():
    parameter = {'username': 'collosorbo', 'password': '10sorbo19', 'start_date': '2019-07-19',
                 'end_date': '2019-07-25'}
    response = requests.post('https://live.netsens.it/export/xml_export_1A.php', data=parameter)
    root = ElementTree.fromstring(response.content)
    station = root[0]
    unit = station[0]
    sensors = unit.findall('sensore')
    s = sensors[0]
    misures = s.findall('misura')
    pressione = []
    for m in misures:
        pressione.append({'date': m.get('data_ora'), 'value': m.get('valore')})
    print(pressione)
    return pressione


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
    unit_list = station_elem.findall('unita')
    if len(unit_list) != 2:
        return 'Sensor unities error (' + str(len(unit_list)) + '/2)'

    weather_date_list = station_elem[0].findall('giorno')
    ground_dates_list = station_elem[1].findall('giorno')
    debug_data = []
    for date_elem in weather_date_list:
        sensor_list = date_elem.findall('sensore')
        ground_date = next((x for x in ground_dates_list if x.get('data') == date_elem.get('data')), None)
        if ground_date is not None:
            sensor_list += ground_date.findall('sensore')

        string = ''
        for sensor_reading in sensor_list:
            sensor = Sensor.objects.get(name__exact=sensor_reading.get('nome'))
            data, created = DailyData.objects.get_or_create(date=date_elem.get('data'), sensor=sensor)

            if sensor.values:
                data.avg = sensor_reading.get('media')
                data.max = sensor_reading.get('massima')
                data.maxTime = sensor_reading.get('ora_massima')
                data.min = sensor_reading.get('minima')
                data.minTime = sensor_reading.get('ora_minima')
            if sensor.tot:
                data.tot = sensor_reading.get('cumulato')
            data.save()
            string += sensor_reading.get('nome') + ' ' + str(created)

        debug_data.append(date_elem.get('data') + '  ' + string)

    debug_data.append(start_date + '   ' + end_date)
    return debug_data
