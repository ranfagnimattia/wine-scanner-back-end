from django.urls import path

from WineApp import views

app_name = 'WineApp'
urlpatterns = [
    path('', views.index, name='index'),
    path('update/daily', views.update_daily_data, name='update.daily'),
    path('update/realtime', views.update_realtime_data, name='update.realtime'),
    path('<field>/predict', views.prediction, name='predict'),
    path('<field>/lstm', views.lstm, name='lstm'),
    path('<field>/decompose', views.decompose, name='decompose'),
    path('correlation', views.correlation, name='correlation')
]
