import json
from django.shortcuts import render
from django.http import JsonResponse
from MontalcinoForecastsApp.views import ajax_get_best_regressors,ajax_get_forecast
from django.views.decorators.csrf import csrf_exempt
from WineApp.models import DailyData
from django.db.models import Avg


# Create your views here.
@csrf_exempt
def winegetForApi(request):
    start_date_str = request.POST.get('startDate')
    end_date_str = request.POST.get('endDate')
    forecast_year = request.POST.get('forecastYear')
    response = ajax_get_best_regressors(request)
    content = json.loads(str(response.content)[2:-1])
    if not(content.get('results') is None):
        try:
            regr_combo = content["results"][0]["regr_combo"]
            result = ajax_get_forecast(request,start_date_str,end_date_str,regr_combo)
            result_content = json.loads(str(result.content)[2:-1])
            print()
            result_content["umidlugott"] = round((DailyData.objects.filter(sensor=2,date__range=(str(2005 if int(forecast_year)-1 == 2004 else int(forecast_year)-1)+'-07-01', str(2015 if int(forecast_year)-1 == 2004 else int(forecast_year)-1)+'-10-01')).aggregate(Avg('avg')))["avg__avg"], 2)
            result_content["umidaprott"] = round((DailyData.objects.filter(sensor=2,date__range=(str(2005 if int(forecast_year)-1 == 2004 else int(forecast_year)-1)+'-04-01', str(2015 if int(forecast_year)-1 == 2004 else int(forecast_year)-1)+'-10-01')).aggregate(Avg('avg')))["avg__avg"], 2)
            result_content["ventoaprott"] = round((DailyData.objects.filter(sensor=7,date__range=(str(2005 if int(forecast_year)-1 == 2004 else int(forecast_year)-1)+'-04-01', str(2015 if int(forecast_year)-1 == 2004 else int(forecast_year)-1)+'-10-01')).aggregate(Avg('avg')))["avg__avg"], 2)
            return JsonResponse(result_content)
        except (json.JSONDecodeError):
            regr_combo = content["results"][0]["regr_combo"]
            result = ajax_get_forecast(request,start_date_str,end_date_str,regr_combo)
            return result
    else:
        return JsonResponse(content)