from django.shortcuts import render

from WineApp.models import Wine

# Library fo Download Data
import requests
from xml.etree import ElementTree


def index(request):
    wine = Wine.objects.get(pk=2)
    history = list(wine.weatherhistory_set.all()[:10])
    history.append("...")
    history += list(wine.weatherhistory_set.all().order_by('-pk')[:10])[::-1]
    return render(request, 'WineApp/index.html', {'list': history})


def download_sensor_data(request):
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

    return render(request, 'WineApp/download.html', {'dati': pressione})
