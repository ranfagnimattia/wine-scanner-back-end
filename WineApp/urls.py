from django.urls import path

from WineApp import views

app_name = 'WineApp'
urlpatterns = [
    # Index Dashboard
    path('', views.show_index, name='show.index'),
    path('ajax/getIndex', views.ajax_get_index, name='ajax.getIndex'),
    path('ajax/updateIndex', views.ajax_update_index, name='ajax.updateIndex'),

    # Daily Dashboard
    path('dailyData', views.show_daily_data, name='show.dailyData'),
    path('ajax/getDailyData', views.ajax_get_daily_data, name='ajax.getDailyData'),
    path('ajax/updateDailyData', views.ajax_update_daily_data, name='ajax.updateDailyData'),

    # Hourly Dashboard
    path('hourlyData', views.show_hourly_data, name='show.hourlyData'),
    path('ajax/getHourlyData', views.ajax_get_hourly_data, name='ajax.getHourlyData'),
    path('ajax/updateHourlyData', views.ajax_update_hourly_data, name='ajax.updateHourlyData'),

    # Anomalies Dashboard
    path('anomalies', views.show_anomalies, name='show.anomalies'),
    path('ajax/getAnomalies', views.ajax_get_anomalies, name='ajax.getAnomalies'),
    path('ajax/updateAnomalies', views.ajax_update_anomalies, name='ajax.updateAnomalies')
]
