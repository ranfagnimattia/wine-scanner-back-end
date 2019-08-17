from datetime import datetime, timedelta
from xml.etree import ElementTree

import requests

from WineApp.models import DailyData, Sensor, RealTimeData, LastUpdate


def update_daily_data() -> dict:
    try:
        start_date = DailyData.objects.latest('date').date
        start_date = datetime.combine(start_date, datetime.min.time())
    except DailyData.DoesNotExist:
        start_date = datetime(2019, 7, 17)
    if start_date < datetime(2019, 7, 17):
        start_date = datetime(2019, 7, 17)
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = datetime.now()
    try:
        parameter = {'username': 'collosorbo', 'password': '10sorbo19', 'start_date': start_date,
                     'end_date': end_date.strftime('%Y-%m-%d'), 'day_average': '1'}
        response = requests.post('https://live.netsens.it/export/xml_export_1A.php', data=parameter)
    except ConnectionError:
        return {'error': 'Errore connessione'}

    if response.status_code != requests.codes.ok:
        return {'error': 'Errore connessione'}
    root_elem = ElementTree.fromstring(response.content)
    if root_elem.get('errore') != '0':
        return {'error': 'Errore API: ' + root_elem.get('messaggio')}
    station_elem = root_elem[0]

    new_data = []
    for unit_elem in station_elem.findall('unita'):
        for date_elem in unit_elem.findall('giorno'):
            for sensor_elem in date_elem.findall('sensore'):
                try:
                    sensor = Sensor.objects.get(name=sensor_elem.get('nome'))
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
                    new_data.append(data)
                except Sensor.DoesNotExist:
                    pass

    last_day = DailyData.objects.filter(date__gte=start_date)
    n_updated = last_day.count()
    last_day.delete()
    DailyData.objects.bulk_create(new_data)
    LastUpdate.objects.update_or_create(type='daily', defaults={'time': end_date})
    return {'updated': n_updated, 'created': len(new_data) - n_updated}


def update_realtime_data() -> dict:
    try:
        start_date = RealTimeData.objects.latest('time').time
    except RealTimeData.DoesNotExist:
        start_date = datetime(2019, 7, 17)
    end_date = datetime.now()

    new_data = []
    while start_date < end_date:
        start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        start_date += timedelta(days=6)
        end_str = start_date.strftime('%Y-%m-%d %H:%M:%S')

        try:
            parameter = {'username': 'collosorbo', 'password': '10sorbo19', 'start_date': start_str,
                         'end_date': end_str}
            response = requests.post('https://live.netsens.it/export/xml_export_1A.php', data=parameter)
        except ConnectionError:
            return {'error': 'Errore connessione'}

        if response.status_code != requests.codes.ok:
            return {'error': 'Errore connessione'}
        root_elem = ElementTree.fromstring(response.content)
        if root_elem.get('errore') != '0':
            return {'error': 'Errore API: ' + root_elem.get('messaggio')}
        station_elem = root_elem[0]

        for unit_elem in station_elem.findall('unita'):
            for sensor_elem in unit_elem.findall('sensore'):
                try:
                    sensor = Sensor.objects.get(name=sensor_elem.get('nome'))
                    for measure_elem in sensor_elem.findall('misura'):
                        if not RealTimeData.objects.filter(time=measure_elem.get('data_ora'),
                                                           sensor=sensor).exists():
                            if sensor.name == 'Pressione atmosferica':
                                value = round(float(measure_elem.get('valore')) / 10, 3)
                            else:
                                value = measure_elem.get('valore')
                            new_data.append(RealTimeData(time=measure_elem.get('data_ora'),
                                                         sensor=sensor, value=value))
                except Sensor.DoesNotExist:
                    pass

    RealTimeData.objects.bulk_create(new_data)
    LastUpdate.objects.update_or_create(type='realtime', defaults={'time': end_date})
    return {'created': len(new_data)}


def get_last_update(update_type: str):
    try:
        last_datetime = LastUpdate.objects.get(type=update_type).time
        return {'date': _relative_date(last_datetime), 'time': last_datetime.strftime('%H:%M')}
    except LastUpdate.DoesNotExist:
        return {'date': '', 'time': ''}


# Private
def _relative_date(date: datetime):
    diff = datetime.today().date() - date.date()
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
