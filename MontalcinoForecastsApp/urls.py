from django.urls import path

from MontalcinoForecastsApp import views

app_name = 'MontalcinoForecastsApp'
urlpatterns = [
    path('', views.simplified, name='simplified'),
    path('complete', views.complete, name='complete'),
    path('help', views.help_page, name='help'),
    path('ajax/getBestRegressors', views.ajax_get_best_regressors, name='ajax_get_best_regressors'),
    path('ajax/getForecast', views.ajax_get_forecast, name='ajax_get_forecast'),
    path('ajax/getBestRegressors/<str:stD>&<str:stE>', views.ajax_get_best_regressors, name='ajax_get_best_regressors'),
    path('ajax/getForecast', views.ajax_get_forecast, name='ajax_get_forecast')
]
