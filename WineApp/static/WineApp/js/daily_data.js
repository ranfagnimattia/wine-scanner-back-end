$('document').ready(function () {
    console.log(data_py);
    updateChart(data_py.sensor, data_py.data);

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
                    updateChart(response.sensor, response.data);
                }
            }
        });
    });
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
