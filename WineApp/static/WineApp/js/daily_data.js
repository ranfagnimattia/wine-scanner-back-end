$('document').ready(function () {
    console.log('all data');
    console.log(data_py);

    console.log(data_py.lastMonthMean);


    let monthData = data_py.lastMonth;
    let diff = data_py.diff;
    let sensor = data_py.sensor;

    updateDashboard(data_py, monthData, diff);

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
                    diff = response.diff;
                    sensor = response.sensor;

                    updateDashboard(response, monthData, diff);
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
            updateOtherChart(sensor, diff, 'trend-chart', measure)
    });


    $('#update-now').click(() => {
        $.getJSON({
            url: data_py.update_url,
            data: {
                'sensor_id': sensor.id
            },
            success: function (response) {
                if (response) {
                    console.log('Info', response.info);

                    monthData = response.lastMonth;
                    diff = response.diff;
                    sensor = response.sensor;

                    updateDashboard(response, monthData, diff);
                }
            }, error: function (response) {
                console.error(response);
            }
        });
    });
});

function updateDashboard(data, monthData, diff) {
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
    $('.js-update').text(data.update);

    // $('.js-last-tot').text(data.last.tot);
    // $('.js-last-max').text(data.last.max);
    // $('.js-last-avg').text(data.last.avg);
    // $('.js-last-min').text(data.last.min);
    let trendSpace = setTrend($('.js-trend-space'), sensor, data.last, data.monthMean);
    trendSpace[0].text(trendSpace[1].toFixed(2) + '0');
    if (sensor.tot) {
        $('.js-last-space').text(data.last.tot.toFixed(2) + '0');
        $('.js-monthMean-space').text(data.monthMean.tot.toFixed(2) + '0');
    } else {
        $('.js-last-space').text(data.last.max.toFixed(2) + '0');
        $('.js-monthMean-space').text(data.monthMean.max.toFixed(2) + '0');
    }
    animateValues([
        [$('.js-last-tot'), data.last.tot],
        [$('.js-last-max'), data.last.max],
        [$('.js-last-avg'), data.last.avg],
        [$('.js-last-min'), data.last.min],
        [$('.js-monthMean-tot'), data.monthMean.tot],
        [$('.js-monthMean-max'), data.monthMean.max],
        [$('.js-monthMean-avg'), data.monthMean.avg],
        [$('.js-monthMean-min'), data.monthMean.min],
        setTrend($('.js-trend-day'), sensor, data.last, data.yesterday),
        setTrend($('.js-trend-week'), sensor, data.last, data.weekMean),
        setTrend($('.js-trend-month'), sensor, data.last, data.monthMean)
    ]);


    // $('.js-monthMean-tot').text(data.monthMean.tot);
    // $('.js-monthMean-max').text(data.monthMean.max);
    // $('.js-monthMean-avg').text(data.monthMean.avg);
    // $('.js-monthMean-min').text(data.monthMean.min);


    // setTrend($('.js-trend-day'), sensor, data.last, data.yesterday);
    // setTrend($('.js-trend-week'), sensor, data.last, data.weekMean);
    // setTrend($('.js-trend-month'), sensor, data.last, data.monthMean);


    updateChart(sensor, data.data);
    setUpButton(sensor);
    updateOtherChart(sensor, monthData, 'month-chart');
    // Passare i dati dell'andamento generale al posto di month chart
    updateOtherChart(sensor, diff, 'trend-chart');
}


function animateValues(valuesPair) {
    const initValues = {};
    const elements = {};
    const finalValues = {};
    valuesPair.forEach((pair, i) => {
        initValues[i] = 0;
        elements[i] = pair[0];
        finalValues[i] = pair[1];
    });
    $(initValues).animate(finalValues, {
        duration: 1000,
        easing: 'easeOutQuart',
        step: function () {
            for (let prop in this)
                if (this.hasOwnProperty(prop))
                    elements[prop].text(this[prop].toFixed(2))
        }
    });
}


function setTrend(elem, sensor, last, mean) {
    let trend;
    if (sensor.tot)
        trend = last.tot - mean.tot;
    else
        trend = last.avg - mean.avg;
    // elem.find('.js-trend').text(trend.toFixed(2));

    if (trend > 0)
        elem.find('.js-trend-icon').html('<i class="fas fa-caret-up"></i>');
    else if (trend < 0)
        elem.find('.js-trend-icon').html('<i class="fas fa-caret-down"></i>');
    else
        elem.find('.js-trend-icon').html('<i class="fas fa-minus"></i>');

    return [elem.find('.js-trend'), trend]
}

function updateChart(sensor, data) {
    let plot;
    let subcaption;
    let schema;
    const chartElem = $('#sensor-chart');
    if (sensor.tot && sensor.values) {
        schema = [
            {
                name: "Time",
                type: "date",
                format: "%Y-%m-%d"
            },
            {
                name: "Tot",
                type: "number"
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
        subcaption = ' avg, tot, max, min';
        plot = [{"value": "Tot"}, {"value": "Avg"}, {"value": "Max"}, {"value": "Min"}];
    } else {
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
            plot = [{"value": "Avg"}, {"value": "Max"}, {"value": "Min"}];
        }
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
    let colors = {"month-chart": themeColors.color2, "trend-chart": themeColors.color3};
    let plot;
    let subcaption;
    let schema;
    let chartData;
    let format = {"suffix": sensor.unit};
    const chartElem = $('#' + id);
    console.log('monthdata');
    console.log(data);
    if (sensor.tot && sensor.values) {
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
        plot = {"value": measure.charAt(0).toUpperCase() + measure.slice(1)};
        chartData = getMeasure(measure, data)
    } else {
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
            plot = {"value": "Tot"};
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
            plot = {"value": measure.charAt(0).toUpperCase() + measure.slice(1)};
            chartData = getMeasure(measure, data)
        }
    }
    if (id === "trend-chart") {
        plot["type"] = "column";
    } else {
        plot['type'] = 'smooth-area';
    }

    const fusionDataStore = new FusionCharts.DataStore();
    const fusionTable = fusionDataStore.createDataTable(chartData, schema);

    chartElem.find('.js-sensor-category').text(subcaption);

    plot['style'] = {'area': {"fill-opacity": 0.15}};
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
                paletteColors: colors[id],
                "showLegend": "0"
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
    if (sensor.tot && sensor.values) {
        $('.values').removeAttr("disabled");
        $('.tot').removeAttr("disabled");
        $('#trend-avg').addClass("active");
        $('#month-avg').addClass("active");
    } else {
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
