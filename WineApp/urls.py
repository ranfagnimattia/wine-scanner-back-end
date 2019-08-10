from django.urls import path

from WineApp import views

app_name = 'WineApp'
urlpatterns = [
    path('', views.index, name='index'),
    # Data from db
    path('dailyData', views.show_daily_data, name='show.dailyData'),

    path('update/daily', views.update_daily_data, name='update.daily'),
    path('update/realtime', views.update_realtime_data, name='update.realtime'),

    # Algorithms
    path('<field>/<measure>/expsmoothing', views.expsmoothing, name='expsmoothing'),
    # es airTemperature/avg/expsmoothing
    path('<field>/<measure>/lstm', views.lstm, name='lstm'),
    # es airTemperature/avg/lstm
    path('<field>/decompose', views.decompose, name='decompose'),
    path('correlation', views.correlation, name='correlation'),

    # Ajax
    path('ajax/getDailyData', views.ajax_get_daily_data, name='ajax.getDailyData'),
    path('ajax/updateDailyData', views.ajax_update_daily_data, name='ajax.updateDailyData')
]
