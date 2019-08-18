from django.urls import path

from WineApp import views

app_name = 'WineApp'
urlpatterns = [
    path('', views.index, name='index'),

    # Daily Dashboard
    path('dailyData', views.show_daily_data, name='show.dailyData'),
    path('ajax/getDailyData', views.ajax_get_daily_data, name='ajax.getDailyData'),
    path('ajax/updateDailyData', views.ajax_update_daily_data, name='ajax.updateDailyData'),

    # RealTime Dashboard
    path('realTimeData', views.show_realtime_data, name='show.realTimeData'),
    path('ajax/getRealTimeData', views.ajax_get_realtime_data, name='ajax.getRealTimeData'),
    path('ajax/updateRealTimeData', views.ajax_update_realtime_data, name='ajax.updateRealTimeData'),

    # Anomalies Dashboard
    path('anomalies', views.show_anomalies, name='show.anomalies'),
    path('ajax/getAnomalies', views.ajax_get_anomalies, name='ajax.getAnomalies'),
    path('ajax/updateAnomalies', views.ajax_update_anomalies, name='ajax.updateAnomalies'),

    # Algorithms
    path('<field>/<measure>/expsmoothing', views.expsmoothing, name='expsmoothing'),
    # es airTemperature/avg/expsmoothing
    path('<field>/<measure>/lstm', views.lstm, name='lstm'),
    # es airTemperature/avg/lstm
    path('<field>/decompose', views.decompose, name='decompose'),
    path('correlation', views.correlation, name='correlation')
]
