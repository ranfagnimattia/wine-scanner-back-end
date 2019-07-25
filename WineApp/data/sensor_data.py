from xml.etree import ElementTree

import requests
from django.utils import timezone

from WineApp.models import DailySensorData


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
        start_date = DailySensorData.objects.latest('date').date.strftime('%Y-%m-%d')
    except DailySensorData.DoesNotExist:
        start_date = '2019-07-17'
    end_date = timezone.localtime().strftime('%Y-%m-%d')
    parameter = {'username': 'collosorbo', 'password': '10sorbo19', 'start_date': start_date,
                 'end_date': end_date, 'day_average': '1'}
    response = requests.post('https://live.netsens.it/export/xml_export_1A.php', data=parameter)

    if response.status_code != requests.codes.ok:
        return 'Request error'
    root = ElementTree.fromstring(response.content)
    if root.get('errore') != '0':
        return 'API error: ' + root.get('messaggio')
    station = root[0]
    units = station.findall('unita')
    if len(units) != 2:
        return 'Sensor unities error (' + str(len(units)) + '/2)'

    weather_unit = station[0]
    ground_unit = station[1]
    weather_dates = weather_unit.findall('giorno')
    ground_dates = ground_unit.findall('giorno')
    sensor_data = []
    for date in weather_dates:
        sensors = date.findall('sensore')
        ground_date = next((x for x in ground_dates if x.get('data') == date.get('data')), None)
        if ground_date is not None:
            sensors += ground_date.findall('sensore')

        data = DailySensorData(date=date.get('data'))
        for sensor in sensors:
            name = sensor.get('nome')
            if name == 'Pressione atmosferica':
                _set_sensor_data(data, sensor, 'pressure')
            elif name == 'Direzione vento':
                _set_sensor_data(data, sensor, 'windDirection')
            elif name == 'Bagnatura fogliare sup':
                _set_sensor_data(data, sensor, 'upperLeafWetness')
            elif name == 'Bagnatura fogliare inf':
                _set_sensor_data(data, sensor, 'lowerLeafWetness')
            elif name == 'Radiazione solare':
                _set_sensor_data(data, sensor, 'solarRadiation')
            elif name == 'Velocità vento':
                _set_sensor_data(data, sensor, 'windSpeed')
            elif name == 'Temperatura aria':
                _set_sensor_data(data, sensor, 'airTemperature')
            elif name == 'Umidità aria':
                _set_sensor_data(data, sensor, 'airHumidity')
            elif name == 'Pioggia':
                _set_sensor_data(data, sensor, 'rain')
                data.rainTot = sensor.get('cumulato')
            elif name == 'Raffica vento':
                _set_sensor_data(data, sensor, 'gustOfWind')
            elif name == 'Punto di rugiada':
                _set_sensor_data(data, sensor, 'dewPoint')
            elif name == 'ET':
                data.ETTot = sensor.get('cumulato')
            elif name == 'Temperatura suolo':
                _set_sensor_data(data, sensor, 'groundTemperature')
            elif name == 'Umidità suolo':
                _set_sensor_data(data, sensor, 'groundHumidity')
        data.save()
        sensor_data.append(date.get('data') + '  ' + sensors[6].get('media') + str([s.get('nome') for s in sensors]))

    sensor_data.append(start_date + '   ' + end_date)
    return sensor_data


def _set_sensor_data(data, sensor, name):
    setattr(data, name + 'Avg', sensor.get('media'))
    setattr(data, name + 'Max', sensor.get('massima'))
    setattr(data, name + 'MaxTime', sensor.get('ora_massima'))
    setattr(data, name + 'Min', sensor.get('minima'))
    setattr(data, name + 'MinTime', sensor.get('ora_minima'))
