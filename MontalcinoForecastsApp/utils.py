from sklearn.impute import SimpleImputer
from MontalcinoForecastsApp.fusioncharts import FusionCharts

from MontalcinoForecastsApp.models import *


def get_regr_combo(post_data):
    regr_combo = []
    regressors_ids = ClimaticIndex.objects.values_list('id', flat=True)
    for id in regressors_ids:
        if post_data.get("regr-" + str(id)) is not None:
            regr_combo.append(id)
    return regr_combo


def get_vintages_list(start_date, end_date):
    start_year = start_date.year
    end_year = end_date.year
    query_set = Vintage.objects.filter(year__gte=start_year, year__lte=end_year)
    if query_set:
        if query_set.count() != end_year - start_year + 1:
            return None
        vals_list = [ob.value for ob in query_set]
        return vals_list
    else:
        return None


def get_data(start_date, end_date, regr_combo):
    regr_list = []
    failed_regr_list = []
    x = np.ones(end_date.year - start_date.year + 1)
    for regr_id in regr_combo:
        regr = ClimaticIndex.objects.get(pk=regr_id)
        values_list = regr.get_list(start_date, end_date)
        if values_list is None or (values_list.count(np.nan) is len(values_list) - 1 and len(values_list) is not 1):
            failed_regr_list.append(regr.name)
        else:
            regr_list.append(regr.name)
            x = np.column_stack((x, values_list))
    if len(regr_list) > 0:
        # Remove first column of ones (constant for regression added later)
        x = np.delete(x, 0, 1)
        # Imputation of missing values
        imp = SimpleImputer(missing_values=np.nan, strategy='mean')
        x = imp.fit_transform(x)
    return x, regr_list, failed_regr_list


def get_icons(regr_combo):
    icons_list = []
    for regr_id in regr_combo:
        regr = ClimaticIndex.objects.get(pk=regr_id)
        icons_list.append(regr.sensor.icon)
    return icons_list


def create_quality_chart(x, y):
    if len(x) is not len(y):
        return None

    data_source = {}
    data_source['chart'] = {
        "xAxisName": "Qualità reale",
        "yAxisName": "Qualità predetta",
        "xAxisMinValue": 1,
        "yAxisMinValue": 1,
        "xAxisMaxValue": 5,
        "yAxisMaxValue": 5,
        "theme": "candy",
        "showLegend": 0,
        "bgColor": "#27293d",
        "plotToolText": "<b>Qualità predetta:</b> $yDataValue<br><b>Qualità reale:</b> $xDataValue",
    }
    data_source['categories'] = [
        {
            "category": [
                {
                    "x": "1",
                    "label": "1",
                    "showVerticalLine": "0"
                },
                {
                    "x": "2",
                    "label": "2"
                },
                {
                    "x": "3",
                    "label": "3"
                },
                {
                    "x": "4",
                    "label": "4"
                },
                {
                    "x": "5",
                    "label": "5"
                }
            ]
        }
    ]
    data_source['dataset'] = [
        {
            "anchorSides": 0,
            "anchorbgcolor": "#f5aa42",
            "anchorBorderColor": "#f5aa42",
            "anchorBorderHoverAlpha": 0,
            "anchorBgHoverColor": "#f5aa42",
        }
    ]
    data_source['dataset'][0]['data'] = []
    for x_val, y_val in zip(x, y):
        data = {}
        data['x'] = x_val
        data['y'] = y_val
        data_source['dataset'][0]['data'].append(data)

    data_source['dataset'].append({
        "showRegressionLine": "1",
        "drawAnchors": "0",
        "regressionLineColor": "#ff6600",
        "regressionLineThickness": "2",
        'data': [
            {
                "x": "1",
                "y": "1"
            },
            {
                "x": "2",
                "y": "2"
            },
            {
                "x": "3",
                "y": "3"
            },
            {
                "x": "4",
                "y": "4"
            },
            {
                "x": "5",
                "y": "5"
            }
        ]
    })

    return FusionCharts("scatter", "chart1", "100%", "100%", "chart", "json", data_source)
