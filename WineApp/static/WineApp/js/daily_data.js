let data;
try {
    data = JSON.parse(document.getElementById('data').textContent);
} catch (e) {

}

if (data) {
    console.log(data);
} else {
    console.log("No data");
}

$('document').ready(function () {
    $('#sensors').on('change', function () {
        const sensor_id = this.value;
        $.getJSON({
            url: data.ajaxUrl,
            data: {
                'sensor_id': sensor_id
            },
            success: function (response) {
                if (response) {
                    console.log(response);
                    // First we are creating a DataStore
                    const fusionDataStore = new FusionCharts.DataStore();
                    // After that we are creating a DataTable by passing our data and schema as arguments
                    const schema = [
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
                    const fusionTable = fusionDataStore.createDataTable(response.data.data, schema);

                    $('#chart-cont').updateFusionCharts({
                        dataSource: {
                            data: fusionTable,
                            caption: {
                                text: 'Sales Analysis' + sensor_id
                            },
                            subcaption: {
                                text: 'Grocery'
                            },
                            yAxis: [{
                                "plot": [{"value": "Avg"}, {"value": "Min"}, {"value": "Max"}],
                                "format": {"prefix": "$"}, "title": "Avg Value"
                            }]
                        }
                    });
                }
            }
        });
    });


    // First we are creating a DataStore
    const fusionDataStore = new FusionCharts.DataStore();
    // After that we are creating a DataTable by passing our data and schema as arguments
    const schema = [
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
    const fusionTable = fusionDataStore.createDataTable(data.data, schema);

    $('#chart-cont').insertFusionCharts({
        type: 'timeseries',
        width: '600',
        height: '400',
        dataFormat: 'json',
        dataSource: {
            data: fusionTable,
            caption: {
                text: 'Sales Analysis'
            },
            subcaption: {
                text: 'Grocery'
            },
            yAxis: [{
                "plot": [{"value": "Avg"}, {"value": "Min"}, {"value": "Max"}],
                "format": {"prefix": "$"}, "title": "Avg Value"
            }]
        }
    });
});