$('document').ready(function () {
    console.log('all data');
    console.log(data_py);

    let sensor = data_py.sensor;
    let monthData = lastMonthData(data_py.data);//test

    updateChart(sensor, data_py.data);
    setUpButton(sensor, 'month');
    setUpButton(sensor, 'trend');
    updateOtherChart(sensor, monthData, 'month-chart');
    // Passare i dati dell'andamento generale al posto di month chart
    updateOtherChart(sensor, monthData, 'trend-chart');

    $('.sensor').on('click', function () {
        console.log("click");
        const sensor_id = $(this).attr('data-sensor');
        $.getJSON({
            url: data_py.ajax_url,
            data: {
                'sensor_id': sensor_id
            },
            success: function (response) {
                if (response) {
                    console.log(response);

                    sensor = response.sensor;
                    monthData = lastMonthData(response.data);

                    updateChart(sensor, response.data);
                    setUpButton(sensor, 'month');
                    setUpButton(sensor, 'trend');
                    updateOtherChart(sensor, monthData, 'month-chart');
                    // Passare i dati dell'andamento generale al posto di month chart
                    updateOtherChart(sensor, monthData, 'trend-chart')
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
        subcaption = sensor.name + ' tot';
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
        subcaption = sensor.name + ' avg, max, min';
        plot = [{"value": "Avg"}, {"value": "Min"}, {"value": "Max"}];
    }
    let caption = sensor.name;
    let format = {"suffix": sensor.unit};

    const fusionDataStore = new FusionCharts.DataStore();
    const fusionTable = fusionDataStore.createDataTable(data, schema);

    $('.active').removeClass("active");
    $('#sensor_' + sensor.id).parent().addClass("active");

    chartElem.find('.card-title').text(caption);
    chartElem.find('.card-category').text(subcaption);
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
/*Aggiorno i frafici secondari*/
function updateOtherChart(sensor, data, id, measure = "Avg") {
    let plot;
    let subcaption;
    let schema;
    let caption;
    let chartData;
    const chartElem = $('#' + id);
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
        subcaption = sensor.name + ' Tot ';
        plot = [{"value": "Tot"}];
        chartData = getMeasure('Tot',data)
    } else {
        schema = [
            {
                name: "Time",
                type: "date",
                format: "%Y-%m-%d"
            },
            {
                name: measure,
                type: "number"
            }];
        subcaption = sensor.name + ' ' + measure;
        plot = [{"value": measure}];
        chartData = getMeasure(measure,data)
    }
    let format = {"suffix": sensor.unit};
    if (id === 'month-chart') {
        caption = 'Ultimo Mese';
    } else {
        caption = 'Andamento';
    }

    const fusionDataStore = new FusionCharts.DataStore();
    const fusionTable = fusionDataStore.createDataTable(chartData, schema);

    chartElem.find('.card-title').text(caption);
    chartElem.find('.card-category').text(subcaption);
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
/* Iniziallizzo i bottoni dei grafici*/
function setUpButton(sensor, id) {
    if (sensor.tot) {
        let tot = $('#' + id + '-tot');
        tot.removeAttr("disabled");
        tot.addClass("active");
        $('#' + id + '-avg').attr("disabled", "disabled");
        $('#' + id + '-min').attr("disabled", "disabled");
        $('#' + id + '-max').attr("disabled", "disabled");
    } else {
        let avg = $('#' + id + '-avg');
        avg.removeAttr("disabled");
        $('#' + id + '-min').removeAttr("disabled");
        $('#' + id + '-max').removeAttr("disabled");
        avg.addClass("active");
        $('#' + id + '-tot').attr("disabled", "disabled")
    }
}
/*Recupero i dati relativi all'ultimo mese*/
function lastMonthData(allData) {
    let len = allData.length;
    let monthData = [];
    for (let i = 30; i > 0; i--) {
        if (i <= len) {
            monthData.push(allData[len - i])
        }
    }
    console.log('lastMonthData');
    console.log(monthData);
    return monthData
}
/*Recupero i dati relativi ad una singola misura max,min,tot o avg*/
function getMeasure(measure,data) {
    let dict = {'Avg':1,'Max':3,'Min':2,'Tot':1};
    let j = dict[measure];
    let measureData = [];
    for(let i=0;i<data.length;i++){
        measureData.push([data[i][0],data[i][j]])
    }
    console.log('measure data '+measure);
    console.log(measureData);
    return measureData
}
