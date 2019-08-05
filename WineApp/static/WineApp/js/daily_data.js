$('document').ready(function () {
    console.log(data_py);
    let sensor = data_py.sensor;
    let schema, caption, subcaption, plot, format;
    let schemaVal = [
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
    let schemaTot = [
            {
                name: "Time",
                type: "date",
                format: "%Y-%m-%d"
            },
            {
                name: "Tot",
                type: "number"
            }];
    if (sensor.tot) {
        schema = schemaTot;
        subcaption = sensor.name + ' tot';
        plot = [{"value": "Tot"}];
    } else {
        schema = schemaVal;
        subcaption = sensor.name + ' avg, max, min';
        plot = [{"value": "Avg"}, {"value": "Min"}, {"value": "Max"}];
    }
    caption = sensor.name;
    format = {"suffix": sensor.unit};

    const fusionDataStore = new FusionCharts.DataStore();

    $('#sensors').on('change', function () {
        const sensor_id = this.value;
        $.getJSON({
            url: data_py.ajax_url,
            data: {
                'sensor_id': sensor_id
            },
            success: function (response) {
                if (response) {
                    console.log(response);
                    let sensor = response.sensor;
                    if (sensor.tot) {
                        schema = schemaTot;
                        subcaption = sensor.name + ' tot';
                        plot = [{"value": "Tot"}];
                    } else {
                        schema = schemaVal;
                        subcaption = sensor.name + ' avg, max, min';
                        plot = [{"value": "Avg"}, {"value": "Min"}, {"value": "Max"}];
                    }
                    caption = sensor.name;
                    format = {"suffix": sensor.unit};

                    const fusionTable = fusionDataStore.createDataTable(response.data, schema);

                    $('#chart-cont').updateFusionCharts({
                        dataSource: {
                            data: fusionTable,
                            caption: {
                                text: caption
                            },
                            subcaption: {
                                text: subcaption
                            },
                            yAxis: [{
                                "plot": plot,
                                "format": format, "title": caption
                            }]
                        }
                    });
                }
            }
        });
    });

    // First we are creating a DataStore
    // After that we are creating a DataTable by passing our data and schema as arguments
    const fusionTable = fusionDataStore.createDataTable(data_py.data, schema);

    $('#chart-cont').insertFusionCharts({
        type: 'timeseries',
        width: '600',
        height: '400',
        dataFormat: 'json',
        dataSource: {
            data: fusionTable,
            caption: {
                text: caption
            },
            subcaption: {
                text: subcaption
            },
            yAxis: [{
                "plot": plot,
                "format": format, "title": caption
            }]
        }
    });
});
