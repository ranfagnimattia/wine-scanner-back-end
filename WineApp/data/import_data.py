from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from django.http import Http404

from WineApp.models import WeatherHistory
from WineApp.models import DailyData
from WineApp.models import Sensor


def download_data():
    df = pd.read_excel('AllData05-19.xlsx')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    print(df.dtypes)
    print(len(df))
    for i in range(0,len(df)):
        x = df.loc[i]
        date = x['Date']
        print(date)
        _save_into_db(date, x['Tavg'], x['Tmax'], x['Tmin'], np.NaN, 'Temperatura aria')
        _save_into_db(date, x['Havg'], x['Hmax'], x['Hmin'], np.NaN, 'Umidità aria')
        _save_into_db(date, x['Dewavg'], x['Dewmax'], x['Dewmin'], np.NaN, 'Punto di rugiada')
        bfsavg = (x['Bfsavg']/24)*100
        _save_into_db(date, bfsavg, x['Bfsmax'], x['Bfsmin'], np.NaN, 'Bagnatura fogliare sup')
        bfiavg = (x['Bfiavg']/24)*100
        _save_into_db(date, bfiavg, x['Bfimax'], x['Bfimin'], np.NaN, 'Bagnatura fogliare inf')
        _save_into_db(date, np.NaN, np.NaN, np.NaN, x['Raintot'], 'Pioggia')
        _save_into_db(date, x['Windavg'], x['Windmax'], x['Windmin'], np.NaN, 'Velocità vento')


def _save_into_db(date, avg, max, min, tot, sensor):
    if np.isnan(avg) and np.isnan(min) and np.isnan(max) and np.isnan(tot):
        return
    else:
        idS = Sensor.objects.get(name=sensor)
        measure = DailyData(date=date, sensor=idS)
        measure.avg = avg
        measure.min = min
        measure.max = max
        measure.tot = tot
        measure.save()
        return


def my_agg(x):
    names = {
        'T avg': x['T'].mean(),
        'T min': x['T'].min(),
        'T max': x['T'].max(),
        'H avg': x['U'].mean(),
        'H min': x['U'].min(),
        'H max': x['U'].max(),
        'Dew avg': x['Td'].mean(),
        'Dew min': x['Td'].min(),
        'Dew max': x['Td'].max(),
        'Wind avg': x['Ff'].mean(),
        'Wind min': x['Ff'].min(),
        'Wind max': x['Ff'].max(),
        'Rain tot': x['RRR'].sum()
    }

    return pd.Series(names, index=['T avg', 'T min', 'T max', 'H avg', 'H min', 'H max', 'Dew avg', 'Dew min',
                                   'Dew max', 'Wind avg', 'Wind min', 'Wind max', 'Rain tot'])


def import_history():
    actual, dates = _get_series('airTemperatureMax')
    # tiezzi = WeatherHistory.objects.filter(date__gte='2018-02-01', wine_id__exact=1)
    # tiezzi = list(tiezzi.values_list('temperatureMax', flat=True))
    # tiezzi = [(f - 32) * 5/9 +3for f in tiezzi]

    print('Reading')
    df = pd.read_excel(r'Grosseto05-16.xlsx', sheet_name='Sheet1')
    print('Done')
    df['Date'] = [datetime.strptime(time, '%d.%m.%Y %H:%M').strftime('%Y-%m-%d') for time in df['Datetime']]
    df1 = df.groupby(['Date']).apply(my_agg)
    df1.to_excel(r'export_dataframe.xlsx', index=True, header=True)

    plt.figure(figsize=(12, 7), dpi=200)
    plt.title('Grosseto')
    plt.plot(actual, '#000000', label='Actual')
    # plt.plot(tiezzi, '--y', label='Tiezzi')
    plt.plot(df1['T max'], '--r', label='Grosseto')
    plt.legend()
    plt.show()
    # list = []
    # for date in datelist:
    #     data = df.loc[df['Datetime'].date() == date.date()]
    #     list.append(data)
    # df.loc[datetime.date(year=2019, month=1, day=1):datetime.date(year=2019, month=1, day=2)]
    # dt_dates = [datetime.strptime(date, '%d.%m.%Y %H:%M') for date in df['Local time in Grosseto (airport)']]
    return []


def _get_series(field: str):
    seasonal_fields = ['airTemperatureAvg', 'airTemperatureMin', 'airTemperatureMax', 'rainAvg',
                       'windSpeedAvg', 'windSpeedMax', 'dewPointAvg', 'dewPointMax', 'dewPointMin', 'airHumidityAvg']
    if field not in seasonal_fields:
        raise Http404("Field does not exist")
    if field.startswith('dewPoint'):
        train_set = WeatherHistory.objects.filter(date__gte='2017-03-12')
    else:
        train_set = WeatherHistory.objects.filter(date__gte='2018-02-01', date__lte='2019-08-01')
    values_list = list(train_set.values_list(field, flat=True))
    dates_list = list(train_set.values_list('date', flat=True))

    return values_list, dates_list
