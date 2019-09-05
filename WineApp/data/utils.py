import sys
from datetime import datetime, timedelta
from itertools import groupby
from xml.etree import ElementTree

import requests

from WineApp.models import *


def get_date_interval(values, date, start, end=0):
    return values.filter(date__gt=date - timedelta(days=start), date__lte=date - timedelta(days=end))


def get_time_interval(values, date, look_back):
    start = date - timedelta(days=look_back)
    end = date + timedelta(days=1 - look_back)
    val = values.filter(time__gte=start, time__lte=end)
    return val


def server_request(start_date: str, end_date: str, day_average: bool):
    try:
        parameter = {'username': 'collosorbo', 'password': '10sorbo19', 'start_date': start_date,
                     'end_date': end_date, 'day_average': '1' if day_average else '0'}
        response = requests.post('https://live.netsens.it/export/xml_export_1A.php', data=parameter)
    except ConnectionError:
        raise ConnectionError('Errore connessione')

    if response.status_code != requests.codes.ok:
        raise ConnectionError('Errore connessione')
    root_elem = ElementTree.fromstring(response.content)
    if root_elem.get('errore') != '0':
        raise ConnectionError('Errore API: ' + root_elem.get('messaggio'))
    return root_elem[0]


def get_last_update(update_type: str) -> dict:
    try:
        last_datetime = LastUpdate.objects.get(type=update_type).time
        return {'date': _relative_date(last_datetime), 'time': last_datetime.strftime('%H:%M')}
    except LastUpdate.DoesNotExist:
        return {'date': '', 'time': ''}


def sort_and_group(iterable, key=None):
    return groupby(sorted(iterable, key=key), key=key)


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


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
