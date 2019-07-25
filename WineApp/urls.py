from django.urls import path

from WineApp import views

app_name = 'WineApp'
urlpatterns = [
    path('', views.index, name='index'),
    path('download', views.download_sensor_data, name='download')
]
