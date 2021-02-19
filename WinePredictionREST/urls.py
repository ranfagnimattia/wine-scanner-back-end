from django.urls import path

from WinePredictionREST import views

app_name = 'WinePredictionREST'
urlpatterns = [
    path('ajax/getForecast', views.winegetForApi, name='wineBestRegrApi'),
]
