from datetime import datetime, timedelta

from WineApp.data.utils import server_request, str_to_class
from WineApp.models import LastUpdate, Sensor


def update_data() -> dict:
    try:
        start_date = LastUpdate.objects.get(type='hourly').time - timedelta(minutes=5)
    except LastUpdate.DoesNotExist:
        start_date = datetime(2019, 7, 17)
    end_date = datetime.now()

    new_data_count = 0
    while start_date < end_date:
        start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        start_date += timedelta(days=6)
        end_str = start_date.strftime('%Y-%m-%d %H:%M:%S')

        try:
            station_elem = server_request(start_str, end_str, False)
        except ConnectionError:
            return {'error': 'Errore connessione'}

        for unit_elem in station_elem.findall('unita'):
            for sensor_elem in unit_elem.findall('sensore'):
                try:
                    sensor = Sensor.objects.get(name=sensor_elem.get('nome'))
                    table = str_to_class('Hourly' + sensor.table)

                    new_data = []
                    for measure_elem in sensor_elem.findall('misura'):
                        if not table.objects.filter(time=measure_elem.get('data_ora')).exists():
                            if sensor.name == 'Pressione atmosferica':
                                value = round(float(measure_elem.get('valore')) / 10, 3)
                            else:
                                value = measure_elem.get('valore')
                            new_data.append(table(time=measure_elem.get('data_ora'), value=value))
                    table.objects.bulk_create(new_data)
                    new_data_count += len(new_data)
                except Sensor.DoesNotExist:
                    pass

    LastUpdate.objects.update_or_create(type='hourly', defaults={'time': end_date})
    return {'created': new_data_count}
