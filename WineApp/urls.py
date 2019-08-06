from django.urls import path

from WineApp import views

app_name = 'WineApp'
urlpatterns = [
    path('', views.index, name='index'),
    path('showdata', views.show_data, name='showdata'),
    path('update/daily', views.update_daily_data, name='update.daily'),
    path('update/realtime', views.update_realtime_data, name='update.realtime'),
    path('<field>/<measure>/expsmoothing', views.expsmoothing, name='expsmoothing'),
    # es airTemperature/avg/expsmoothing
    path('<field>/<measure>/lstm', views.lstm, name='lstm'),
    # es airTemperature/avg/lstm
    path('<field>/decompose', views.decompose, name='decompose'),
    path('correlation', views.correlation, name='correlation'),
    path('ajax/getDailyData', views.get_daily_data, name='ajax.getDailyData'),
]
