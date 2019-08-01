import numpy as np

from WineApp.models import WeatherHistory


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\33[31m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def correlation():
    fields = ['airTemperatureAvg', 'airTemperatureMax',
              'airTemperatureMin',
              'airHumidityAvg', 'airHumidityMin',
              'airHumidityMax',
              'dewPointAvg', 'dewPointMax', 'dewPointMin',
              'rainAvg', 'windSpeedAvg', 'windSpeedMax']
    data = _get_series(fields)
    corr = np.corrcoef(data, rowvar=False)
    for i, field in enumerate(fields):
        out = bcolors.BLUE + field + bcolors.ENDC + ': '
        out = out.ljust(28)
        for j, f in enumerate(fields):
            if abs(corr[i, j]) > 0.5:
                out += bcolors.GREEN
            elif abs(corr[i, j]) > 0.2:
                out += bcolors.YELLOW
            out += f + ' ' + bcolors.ENDC
        print(out)


def _get_series(fields):
    data = WeatherHistory.objects.filter(date__gte='2017-03-12').values_list(*fields)
    return np.array(data)
