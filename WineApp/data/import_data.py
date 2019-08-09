from datetime import datetime

import numpy as np
import pandas as pd

from WineApp.models import DailyData
from WineApp.models import Sensor


def import_daily_data():
    df = pd.read_excel('AllData05-19.xlsx')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    print(df.dtypes)
    print(len(df))
    new_measures = []
    for i in range(0, len(df)):
        x = df.loc[i]
        date = x['Date']
        print(date)
        _save_into_db(new_measures, date, x['Tavg'], x['Tmax'], x['Tmin'], np.NaN, 'Temperatura aria')
        _save_into_db(new_measures, date, x['Havg'], x['Hmax'], x['Hmin'], np.NaN, 'Umidità aria')
        _save_into_db(new_measures, date, x['Dewavg'], x['Dewmax'], x['Dewmin'], np.NaN, 'Punto di rugiada')
        bfsavg = (x['Bfsavg'] / 24) * 100
        _save_into_db(new_measures, date, bfsavg, x['Bfsmax'], x['Bfsmin'], np.NaN, 'Bagnatura fogliare sup')
        bfiavg = (x['Bfiavg'] / 24) * 100
        _save_into_db(new_measures, date, bfiavg, x['Bfimax'], x['Bfimin'], np.NaN, 'Bagnatura fogliare inf')
        _save_into_db(new_measures, date, np.NaN, np.NaN, np.NaN, x['Raintot'], 'Pioggia')
        _save_into_db(new_measures, date, x['Windavg'], x['Windmax'], x['Windmin'], np.NaN, 'Velocità vento')
    DailyData.objects.bulk_create(new_measures)


def _save_into_db(new_measures, date, avg, max, min, tot, sensor):
    if np.isnan(avg) and np.isnan(min) and np.isnan(max) and np.isnan(tot):
        return
    else:
        sensor = Sensor.objects.get(name=sensor)
        measure = DailyData(date=date, sensor=sensor)
        measure.avg = avg
        measure.min = min
        measure.max = max
        measure.tot = tot
        new_measures.append(measure)
        return


def process_weather_daily_data():
    print('Reading')
    df = pd.read_excel(r'Grosseto05-16.xlsx', sheet_name='Sheet1')
    print('Done')
    df['Date'] = [datetime.strptime(time, '%d.%m.%Y %H:%M').strftime('%Y-%m-%d') for time in df['Datetime']]
    df1 = df.groupby(['Date']).apply(_weather_agg)
    df1.to_excel(r'weather_daily_data.xlsx', index=True, header=True)


def _weather_agg(x):
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
