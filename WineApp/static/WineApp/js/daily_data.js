$('document').ready(function () {
    console.log('all data');
    console.log(data_py);


    let monthData = data_py.lastMonth;
    let sensor = data_py.sensor;

    updateDashboard(data_py, monthData);

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
                    sensor = response.sensor;

                    updateDashboard(response, monthData);
                }
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
            updateOtherChart(sensor, monthData, 'trend-chart', measure)
    })
});

function updateDashboard(data, monthData) {
    $('.js-sensor').text(data.sensor.name);
    console.log('last day');
    console.log(data.last);
    $('.js-sensor-max').text(data.last.max + data.sensor.unit);
    $('.js-sensor-avg').text(data.last.avg + data.sensor.unit);
    $('.js-sensor-min').text(data.last.min + data.sensor.unit);
    updateChart(data.sensor, data.data);
    setUpButton(data.sensor);
    updateOtherChart(data.sensor, monthData, 'month-chart');
    // Passare i dati dell'andamento generale al posto di month chart
    updateOtherChart(data.sensor, monthData, 'trend-chart');
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
    let caption = sensor.name;
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
