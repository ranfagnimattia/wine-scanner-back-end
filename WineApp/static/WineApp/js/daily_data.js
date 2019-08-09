$('document').ready(function () {
    console.log('all data');
    console.log(data_py);


    let monthData = data_py.lastMonth;
    let trendData = data_py.trend;
    let sensor = data_py.sensor;

    updateDashboard(data_py, monthData, trendData);

    $('.sensor').on('click', function () {
        const sensor_id = $(this).attr('data-sensor');
        $.getJSON({
            url: data_py.ajax_url,
            data: {
                'sensor_id': sensor_id
            },
            success: function (response) {
                if (response) {
                    console.log('all data response');
                    console.log(response);

                    monthData = response.lastMonth;
                    trendData = response.trend;
                    sensor = response.sensor;

                    updateDashboard(response, monthData,trendData);
                }
            }, error: function (response) {
                console.error(response);
            }
        });
    });
    /*Gestore dell'evento click sui bottoni del grafico dell'ultimo mese*/
    $('.month').on('click', function () {
        console.log("month click");
        const measure = $(this).attr('data-val');
        if (!$(this).hasClass("active"))
            updateOtherChart(sensor, monthData, 'month-chart', measure)
    });
    /*Gestore dell'evento click sui bottoni del grafico dell'andamento*/
    $('.trend').on('click', function () {
        console.log("trend click");
        const measure = $(this).attr('data-val');
        if (!$(this).hasClass("active"))
            updateOtherChart(sensor, trendData, 'trend-chart', measure)
    });


    $('#update-now').click(() => {
        console.log('Update');
    });
});

function updateDashboard(data, monthData, trendData) {
    const sensor = data.sensor;
    $('.js-sensor').text(sensor.name);
    $('.js-sensor-icon').html('<i class="' + sensor.icon + '"></i>');
    $('.js-unit').html(sensor.unit.replace('^2', '<sup>2</sup>'));

    if (sensor.values)
        $('.js-show-values').show();
    else
        $('.js-show-values').hide();

    if (sensor.tot)
        $('.js-show-tot').show();
    else
        $('.js-show-tot').hide();

    console.log(sensor);
    console.log(data.last);
    $('.js-last-tot').text(data.last.tot);
    $('.js-last-max').text(data.last.max);
    $('.js-last-avg').text(data.last.avg);
    $('.js-last-min').text(data.last.min);

    $('.js-update').text(data.update);

    let trend;
    if (sensor.tot) {
        trend = data.last.tot - data.yesterday.tot;
        $('.js-main-category').text('tot');
    } else {
        trend = data.last.avg - data.yesterday.avg;
        $('.js-main-category').text('avg');
    }
    $('.js-trend').text(trend.toFixed(2));
    if (trend > 0)
        $('.js-trend-icon').html('<i class="fas fa-caret-up"></i>');
    else if (trend < 0)
        $('.js-trend-icon').html('<i class="fas fa-caret-down"></i>');
    else
        $('.js-trend-icon').html('<i class="fas fa-minus"></i>');

    updateChart(sensor, data.data);
    setUpButton(sensor);
    updateOtherChart(sensor, monthData, 'month-chart');
    // Passare i dati dell'andamento generale al posto di month chart
    updateOtherChart(sensor, trendData, 'trend-chart');
}

function updateChart(sensor, data) {
    let plot;
    let subcaption;
    let schema;
    const chartElem = $('#sensor-chart');
    if (sensor.tot) {
        schema = [
            {
                name: "Time",
                type: "date",
                format: "%Y-%m-%d"
            },
            {
                name: "Tot",
                type: "number"
            }];
        subcaption = ' tot';
        plot = [{"value": "Tot"}];
    } else {
        schema = [
            {
                name: "Time",
                type: "date",
                format: "%Y-%m-%d"
            },
            {
                name: "Avg",
                type: "number"
            },
            {
                name: "Min",
                type: "number"
            },
            {
                name: "Max",
                type: "number"
            }];
        subcaption = ' avg, max, min';
        plot = [{"value": "Avg"}, {"value": "Min"}, {"value": "Max"}];
    }
    let format = {"suffix": sensor.unit};

    const fusionDataStore = new FusionCharts.DataStore();
    const fusionTable = fusionDataStore.createDataTable(data, schema);

    $('.active').removeClass("active");
    $('#sensor_' + sensor.id).parent().addClass("active");

    $('.js-sensor-category').text(subcaption);

    chartElem.find('.chart').insertFusionCharts({
        type: 'timeseries',
        width: '100%',
        height: '100%',
        dataFormat: 'json',
        dataSource: {
            chart: {
                theme: 'candy',
            },
            data: fusionTable,
            yAxis: [{
                "plot": plot,
                "format": format,
                title: ''
            }]
        }
    });
}

/*Aggiorno i grafici secondari*/
function updateOtherChart(sensor, data, id, measure = "avg") {
    let colors = {"month-chart": "#e14eca", "trend-chart": "#00f2c3"};
    let plot;
    let subcaption;
    let schema;
    let chartData;
    let format = {"suffix": sensor.unit};
    const chartElem = $('#' + id);
    console.log('monthdata');
    console.log(data);
    if (sensor.tot) {
        schema = [
            {
                name: "Time",
                type: "date",
                format: "%Y-%m-%d"
            },
            {
                name: "Tot",
                type: "number"
            }];
        subcaption = ' tot ';
        plot = [{"value": "Tot", "type": "column"}];
        chartData = getMeasure('tot', data)
    } else {
        schema = [
            {
                name: "Time",
                type: "date",
                format: "%Y-%m-%d"
            },
            {
                name: measure.charAt(0).toUpperCase() + measure.slice(1),
                type: "number"
            }];
        subcaption = ' ' + measure;
        plot = [{"value": measure.charAt(0).toUpperCase() + measure.slice(1)}];
        chartData = getMeasure(measure, data)
    }

    const fusionDataStore = new FusionCharts.DataStore();
    const fusionTable = fusionDataStore.createDataTable(chartData, schema);

    chartElem.find('.js-sensor-category').text(subcaption);
    chartElem.find('.chart').insertFusionCharts({
        type: 'timeseries',
        width: '100%',
        height: '100%',
        dataFormat: 'json',

        dataSource: {
            navigator: {
                enabled: 0
            },

            chart: {
                theme: 'candy',
                paletteColors: colors[id]
            },
            "extensions": {
                "standardRangeSelector": {
                    "enabled": "0"
                },
                "customRangeSelector": {
                    "enabled": "0"
                }
            },
            data: fusionTable,
            yAxis: [{
                "plot": plot,
                "format": format,
                title: ''
            }]
        }
    });
}

/* Iniziallizzo i bottoni dei grafici*/
function setUpButton(sensor) {
    if (sensor.tot) {
        let tot = $('.tot');
        tot.removeAttr("disabled");
        tot.addClass("active");
        $('.values').attr("disabled", "disabled");
    } else {
        $('.values').removeAttr("disabled");
        $('#trend-avg').addClass("active");
        $('#month-avg').addClass("active");
        $('.tot').attr("disabled", "disabled");
    }
}

/*Recupero i dati relativi ad una singola misura max,min,tot o avg*/
function getMeasure(measure, data) {
    let measureData = [];
    for (let i = 0; i < data.length; i++) {
        measureData.push([data[i]['date'], data[i][measure]])
    }
    console.log('measure data ' + measure);
    console.log(measureData);

    return measureData
}
