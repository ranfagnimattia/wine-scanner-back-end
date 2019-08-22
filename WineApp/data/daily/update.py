from datetime import datetime

from WineApp.data.utils import server_request
from WineApp.models import DailyData, Sensor, LastUpdate


def update_data() -> dict:
    try:
        start_date = DailyData.objects.latest('date').date
        start_date = datetime.combine(start_date, datetime.min.time())
    except DailyData.DoesNotExist:
        start_date = datetime(2019, 7, 17)
    if start_date < datetime(2019, 7, 17):
        start_date = datetime(2019, 7, 17)
    end_date = datetime.now()

    try:
        station_elem = server_request(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), True)
    except ConnectionError:
        return {'error': 'Errore connessione'}

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
