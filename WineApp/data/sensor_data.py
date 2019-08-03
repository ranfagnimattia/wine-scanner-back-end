from xml.etree import ElementTree

import requests
from django.utils import timezone
from django.http import Http404
from WineApp.models import DailyData, Sensor, RealTimeData


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


def update_realtime_data():
    try:
        start_date = DailyData.objects.latest('date').date.strftime('%Y-%m-%d')
    except DailyData.DoesNotExist:
        start_date = '2019-07-17'
    end_date = timezone.localtime().strftime('%Y-%m-%d')
    parameter = {'username': 'collosorbo', 'password': '10sorbo19', 'start_date': start_date,
                 'end_date': end_date}
    response = requests.post('https://live.netsens.it/export/xml_export_1A.php', data=parameter)

    if response.status_code != requests.codes.ok:
        return 'Request error'
    root_elem = ElementTree.fromstring(response.content)
    if root_elem.get('errore') != '0':
        return 'API error: ' + root_elem.get('messaggio')
    station_elem = root_elem[0]

    debug_data = []
    for unit_elem in station_elem.findall('unita'):
        for sensor_elem in unit_elem.findall('sensore'):
            try:
                sensor = Sensor.objects.get(name=sensor_elem.get('nome'))
                for measure_elem in sensor_elem.findall('misura'):
                    data, created = RealTimeData.objects.update_or_create(time=measure_elem.get('data_ora'),
                                                                          sensor=sensor,
                                                                          defaults={
                                                                              'value': measure_elem.get('valore')})
                    debug_data.append(
                        str(created) + ': ' + measure_elem.get('data_ora') + '  ' + measure_elem.get('valore'))
            except Sensor.DoesNotExist:
                debug_data.append(sensor_elem.get('nome') + '  NONE')
                pass

    debug_data.append(start_date + '   ' + end_date)
    return debug_data

# todo choose size of train and test set
def _get_series(field: str, measure: str):
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
    # seasonal_fields = ['airTemperatureAvg', 'airTemperatureMin', 'airTemperatureMax', 'rainAvg',
    #                    'windSpeedAvg', 'windSpeedMax', 'dewPointAvg', 'dewPointMax', 'dewPointMin']
    # if field not in seasonal_fields:
    #     raise Http404("Field does not exist")
    # if field.startswith('dewPoint'):
    #     train_set = WeatherHistory.objects.filter(date__gte='2017-03-12')
    # else:
    #     train_set = WeatherHistory.objects.all()
    # train_list = list(train_set.values_list(field, flat=True))
    #
    # test_set = DailyData.objects.all()
    # test_list = list(test_set.values_list(field, flat=True))
    #
    # return train_list, test_list, field in seasonal_fields, test_set.values_list('date', flat=True)
