from django.urls import path

from WineApp import views

app_name = 'WineApp'
urlpatterns = [
    path('', views.index, name='index'),
    path('download', views.download_sensor_data, name='download'),
    path('daily', views.update_daily_sensor_data, name='daily'),
    path('<field>/predict', views.prediction, name='predict'),
    path('<field>/lstm', views.lstm, name='lstm'),
    path('<field>/decompose', views.decompose, name='decompose')
]
