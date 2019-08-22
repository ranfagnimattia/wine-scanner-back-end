from datetime import datetime, timedelta

from WineApp.data.utils import server_request
from WineApp.models import Sensor, RealTimeData, LastUpdate


def update_data() -> dict:
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
            station_elem = server_request(start_str, end_str, False)
        except ConnectionError:
            return {'error': 'Errore connessione'}

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
