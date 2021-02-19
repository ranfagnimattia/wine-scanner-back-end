from datetime import datetime
import statsmodels.api as sm
from more_itertools.recipes import powerset

from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Min, Max
from MontalcinoForecastsApp.utils import *

from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def help_page(request):
    return render(request, "MontalcinoForecastsApp/help.html")


def complete(request):
    earliest_db_str = DailyData.objects.all().aggregate(Min("date")).get('date__min').strftime('%d/%m/%Y')
    latest_db_str = DailyData.objects.all().aggregate(Max("date")).get('date__max').strftime('%d/%m/%Y')
    context = {'start_db': earliest_db_str, 'end_db': latest_db_str}

    form_regressors = ClimaticIndex.objects.all().values('id', 'name')
    context['form_regressors'] = form_regressors

    if request.method == "POST" and request.POST.get('startDate') is not None:

        start_date_str = request.POST.get('startDate')
        end_date_str = request.POST.get('endDate')
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date()
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date()

        # Creation of lists of vintages
        vintages = get_vintages_list(start_date, end_date)
        if vintages is None:
            context['err_msg'] = "Dati sulle annate mancanti tra il " + start_date_str + " e il " + end_date_str
            return render(request, "MontalcinoForecastsApp/complete.html", context)

        # Data array creation
        regr_combo = get_regr_combo(request.POST)
        x, regr_list, failed_regr_list = get_data(start_date, end_date, regr_combo)

        # Error if unable to get all data (all nan or all nan except one)
        if len(failed_regr_list) > 0:
            err_msg = "Dati mancanti o non sufficienti tra il " + start_date_str + " e il " + end_date_str + \
                                 " per poter calcolare i seguenti indici: "
            for regr in failed_regr_list:
                err_msg += regr + ", "
            context['err_msg'] = err_msg[:-2] + "."
            return render(request, "MontalcinoForecastsApp/complete.html", context)

        # Error if no regressor was selected
        if len(regr_list) is 0:
            context['err_msg'] = "Nessun indice selezionato"
            return render(request, "MontalcinoForecastsApp/complete.html", context)

        # Error if more regressors than data
        if len(vintages) <= len(regr_list):
            err_msg = "Pochi anni e troppi regressori, impossibile usare la regressione lineare."
            context['err_msg'] = err_msg
            return render(request, "MontalcinoForecastsApp/complete.html", context)

        # Linear regression
        x2 = sm.add_constant(x, has_constant='add')
        model = sm.OLS(vintages, x2)
        results = model.fit()
        vin_pred = results.predict(x2)

        # Chart and cards data creation
        chart = create_quality_chart(vintages, vin_pred)
        icons = get_icons(regr_combo)
        table_data = list(zip(["Intercetta"] + regr_list, ["fas fa-chart-line"] + icons,
                              results.params, results.pvalues))

        # Update context
        context['start_train_date'] = start_date_str
        context['end_train_date'] = end_date_str
        context['chart_out'] = chart.render()
        context['regr_count'] = len(regr_list)
        context['r2'] = results.rsquared
        context['adj_r2'] = results.rsquared_adj
        context['table_data'] = table_data
        context['anchor'] = "results-section"
        context['regr_combo'] = regr_combo

        return render(request, "MontalcinoForecastsApp/complete.html", context)

    else:
        return render(request, "MontalcinoForecastsApp/complete.html", context)


def simplified(request):
    earliest_db_str = DailyData.objects.all().aggregate(Min("date")).get('date__min').strftime('%d/%m/%Y')
    latest_db_str = DailyData.objects.all().aggregate(Max("date")).get('date__max').strftime('%d/%m/%Y')
    context = {'start_db': earliest_db_str, 'end_db': latest_db_str}
    return render(request, "MontalcinoForecastsApp/simplified.html", context)

@csrf_exempt
def ajax_get_best_regressors(request,stD='',stE=''):
    start_date_str = request.POST.get('startDate',stD)
    end_date_str = request.POST.get('endDate',stE)
    if stD != '':
        start_date = datetime.strptime(start_date_str, "%d-%m-%Y").date()
    else: 
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date()
    if stE != '':
        end_date = datetime.strptime(end_date_str, "%d-%m-%Y").date()
    else:
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date()  
    """
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date()
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date()
    """
    # Creation of lists of vintages and years
    vintages = get_vintages_list(start_date, end_date)
    if vintages is None:
        err_msg = "Dati sulle annate mancanti tra il " + start_date_str + " e il " + end_date_str
        return JsonResponse({"err_msg": err_msg})

    # Get data for all the regressors
    regressors_set = ClimaticIndex.objects.all()
    dict_ids_values_regr = {}
    ids_list = []
    failed_regr_names = []
    for regr in regressors_set:
        values_list = regr.get_list(start_date, end_date)
        if values_list is not None and not (values_list.count(np.nan) is len(values_list) - 1 and
                                            len(values_list) is not 1):
            # Imputation of missing values
            values_list = np.array(values_list).reshape((-1, 1))
            imp = SimpleImputer(missing_values=np.nan, strategy='mean')
            values_list = imp.fit_transform(values_list)

            dict_ids_values_regr[regr.id] = {'values_list': values_list, 'regr': regr}
            ids_list.append(regr.id)
        else:
            failed_regr_names.append(regr.name)

    # Error if no data
    if len(dict_ids_values_regr) is 0:
        err_msg = "Dati meteorologici mancanti tra il " + start_date_str + " e il " + end_date_str
        return JsonResponse({"err_msg": err_msg})

    # Generate all combinations and run all the possible linear regressions
    combo_list = list(powerset(ids_list))
    combo_list.pop(0)
    n_years = len(vintages)
    models_results = []
    for combo in combo_list:
        # Check if observations > regressors
        if n_years > len(combo):
            x = np.ones(end_date.year - start_date.year + 1)
            current_regressors = []
            for id in combo:
                x = np.column_stack((x, dict_ids_values_regr[id]['values_list']))
                current_regressors.append(dict_ids_values_regr[id]['regr'])
            # No need to add the constant
            result = sm.OLS(vintages, x).fit()
            models_results.append({'result': result, 'regr_list': current_regressors})

    # Filter models with all p-values < threshold and sort by adj R^2
    pvalues_threshold = 0.2
    best_pvalues_models = list(filter(lambda mod: all(k <= pvalues_threshold for k in mod["result"].pvalues),
                                      models_results))
    best_pvalues_models.sort(key=lambda mod: mod["result"].rsquared_adj, reverse=True)

    # Alternative: filter models with all p-values < increasing threshold, stop at the smallest and sort by adj R^2
    '''
    best_pvalues_models = []
    pvalues_thresholds = [0.01, 0.05, 0.1, 0.2, 0.3]
    for pvalues_threshold in pvalues_thresholds:
        best_pvalues_models = list(filter(lambda mod: all(k <= pvalues_threshold for k in mod["result"].pvalues),
                                          models_results))
        if len(best_pvalues_models) is not 0:
            best_pvalues_models.sort(key=lambda mod: mod["result"].rsquared_adj, reverse=True)
            break
    '''

    # Error if no match found
    if len(best_pvalues_models) is 0:
        err_msg = "Impossibile determinare il miglior modello tra il " + start_date_str + " e il " + end_date_str + \
                  ". Selezionare un altro range di date."
        return JsonResponse({"err_msg": err_msg})

    # Return the results for the best 4 combinations
    best_results_summary = []
    for mod in best_pvalues_models[:4]:
        content = {}
        content['regr_list'] = [regr.name for regr in mod['regr_list']]
        content['icons'] = [regr.sensor.icon for regr in mod['regr_list']]
        content['regr_combo'] = [regr.id for regr in mod['regr_list']]
        content['adj_r2'] = mod["result"].rsquared_adj
        content['p_values'] = mod["result"].pvalues.tolist()
        best_results_summary.append(content)
    return JsonResponse({"results": best_results_summary, "failed_regressors": failed_regr_names,
                         "pvalues_threshold": pvalues_threshold})

@csrf_exempt
def ajax_get_forecast(request,startDate='',endDate='',regrcombo = []):
    start_date_str = request.POST.get('startTrainDate',startDate)
    end_date_str = request.POST.get('endTrainDate',endDate)
    start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date()
    end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date()

    forecast_year = int(request.POST.get('forecastYear'))
    start_forecast_date = datetime(forecast_year, 1, 1).date()
    end_forecast_date = datetime(forecast_year, 12, 31).date()

    regr_combo = request.POST.getlist('regrCombo[]',regrcombo)

    # Train regression
    vintages = get_vintages_list(start_date, end_date)
    x, regr_list, failed_regr_list = get_data(start_date, end_date, regr_combo)
    x2 = sm.add_constant(x, has_constant='add')
    model = sm.OLS(vintages, x2)
    results = model.fit()

    # Make the prediction
    x, regr_list, failed_regr_list = get_data(start_forecast_date, end_forecast_date, regr_combo)
    if len(failed_regr_list) > 0:
        err_msg = "Dati mancanti per l'anno " + request.POST.get('forecastYear') + " per i seguenti indici: "
        for regr in failed_regr_list:
            err_msg += regr + ", "
        err_msg = err_msg[:-2] + "."
        return JsonResponse({"err_msg": err_msg})
    x2 = sm.add_constant(x, has_constant='add')
    quality = round(results.predict(x2)[0], 2)

    return JsonResponse({"quality": quality, "r2_adj": results.rsquared_adj, "regr_combo": regr_combo,
                         "regr_list": regr_list})
