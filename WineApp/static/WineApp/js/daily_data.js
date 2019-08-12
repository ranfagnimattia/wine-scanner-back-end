/**
 * @param data_py
 * @param data_py.getUrl
 * @param data_py.updateUrl
 * @param data_py.allData
 * @param data_py.categories
 * @param data_py.last
 * @param data_py.lastMonth
 * @param data_py.diff
 * @param data_py.monthMean
 * @param data_py.weekMean
 * @param data_py.yesterday
 * @param data_py.sensor
 *
 * @param response.updated
 * @param response.created
 */

$('document').ready(function () {
    updateDashboard();

    $('.sensor').click(function () {
        $.getJSON({
            url: data_py.getUrl,
            data: {
                'sensor_id': $(this).data('id')
            },
            success: function (response) {
                if (response) {
                    window.data_py = response;
                    updateDashboard();
                }
            }, error: function (response) {
                console.error(response);
            }
        });
    });

    $('.sensor-toggle').click(function () {
        $(this).find('.caret-icon').toggleClass('fa-rotate-180');
        $(this).next('.nav-measures').slideToggle();
    });

    /* Chart buttons click event */
    $('#month-chart .btn').click(function () {
        if (!$(this).hasClass("active"))
            updateChart($('#month-chart'), data_py.lastMonth, $(this).data('category').toLowerCase())
    });
    $('#trend-chart .btn').click(function () {
        if (!$(this).hasClass("active"))
            updateChart($('#trend-chart'), data_py.diff, $(this).data('category').toLowerCase())
    });

    updateData();
});

function updateData() {
    const elem = $('#refresh');
    elem.html('<i class="fas fa-redo fa-spin"></i> <span>Aggiornamento...</span>').removeClass('link').off('click');
    let now = new Date();
    let hr = now.getHours();
    if (hr < 10)
        hr = "0" + hr;
    let min = now.getMinutes();
    if (min < 10)
        min = "0" + min;
    $('.js-last-update').text('Oggi ' + hr + ':' + min);

    $.getJSON({
        url: data_py.updateUrl,
        success: function (response) {
            if (!response || response.error) {
                elem.html('<i class="fas fa-times"></i><span>' +
                    (!response ? 'Errore server' : response.error) + '</span>');
                return;
            }
            if (!response.updated && !response.created) {
                elem.html('<i class="fas fa-check"></i> <span>Tutti i dati sono aggiornati</span>');
                return;
            }
            let msg = 'Ricarica ora ';
            if (response.updated > 0)
                msg += response.updated + ' dati aggiornati';
            if (response.created > 0) {
                if (response.updated > 0)
                    msg += ' e ';
                msg += response.created + ' nuovi dati';
            }
            elem.html('<i class="fas fa-redo"></i> <span>' + msg + '</span>').addClass('link').click(() => {
                elem.html('<i class="fas fa-check"></i> <span>Tutti i dati sono aggiornati</span>')
                    .removeClass('link').off('click');

                $(`.sensor[data-id='${data_py.sensor.id}']`).click();
            });

        }, error: function (response) {
            console.error(response);
        }
    });
}

function updateDashboard() {
    console.log("Data", data_py);

    const refreshElem = $('#refresh');
    if (refreshElem.hasClass('link')) {
        refreshElem.html('<i class="fas fa-check"></i> <span>Tutti i dati sono aggiornati</span>')
            .removeClass('link').off('click');
    }

    const sensor = data_py.sensor;
    const firstCategory = data_py.categories[0].toLowerCase();

    $('.js-sensor').text(sensor.name);
    $('.js-sensor-icon').html('<i class="' + sensor.icon + '"></i>');
    $('.js-unit').html(sensor.unit.replace('^2', '<sup>2</sup>'));

    let trendSpace = setUpTrend($('.js-trend-space'), firstCategory, data_py.last, data_py.monthMean);
    trendSpace[0].text(trendSpace[1].toFixed(2) + '0');
    $('.js-last-space').text(data_py.last[firstCategory].toFixed(2) + '0');
    $('.js-monthMean-space').text(data_py.monthMean[firstCategory].toFixed(2) + '0');

    const animations = [
        setUpTrend($('.js-trend-day'), firstCategory, data_py.last, data_py.yesterday),
        setUpTrend($('.js-trend-week'), firstCategory, data_py.last, data_py.weekMean),
        setUpTrend($('.js-trend-month'), firstCategory, data_py.last, data_py.monthMean)
    ];
    $('[class*="js-show-"]').hide();
    data_py.categories.forEach((c) => {
        const cat = c.toLowerCase();
        $('.js-show-' + cat).show();
        animations.push([$('.js-last-' + cat), data_py.last[cat]]);
        animations.push([$('.js-monthMean-' + cat), data_py.monthMean[cat]]);
    });

    animateValues(animations);

    $('.active').removeClass("active");
    $(`.sensor[data-id='${sensor.id}']`).parent().addClass("active");
    updateBigChart($('#sensor-chart'), data_py.allData);
    setUpChart($('#month-chart'), data_py.lastMonth);
    setUpChart($('#trend-chart'), data_py.diff);

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


function setUpTrend(elem, category, last, mean) {
    const trend = last[category] - mean[category];

    if (trend > 0)
        elem.find('.js-trend-icon').html('<i class="fas fa-caret-up"></i>');
    else if (trend < 0)
        elem.find('.js-trend-icon').html('<i class="fas fa-caret-down"></i>');
    else
        elem.find('.js-trend-icon').html('<i class="fas fa-minus"></i>');

    return [elem.find('.js-trend'), trend]
}

/* Charts */
function updateBigChart(elem, data) {
    let scheme = [];
    scheme.push({
        name: "Time",
        type: "date",
        format: "%Y-%m-%d"
    });
    data_py.categories.forEach((c) => {
        scheme.push({name: c, type: "number"});
    });

    $('.js-sensor-category').text(data_py.categories.join(', '));
    const fusionTable = new FusionCharts.DataStore().createDataTable(data, scheme);

    elem.find('.chart').insertFusionCharts({
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
                "plot": data_py.categories.map((c) => ({value: c})),
                "format": {"suffix": data_py.sensor.unit},
                title: ''
            }]
        }
    });
}


function setUpChart(elem, data) {
    elem.find('.btn').attr("disabled", "disabled");
    data_py.categories.forEach((c, i) => {
        const btn = elem.find(`[data-category='${c}']`);
        btn.removeAttr("disabled");
        if (i === 0) {
            btn.addClass("active");
            updateChart(elem, data, c);
        }
    });
}

function updateChart(elem, data, category) {
    let id = elem.attr('id');
    let styles = {
        "month-chart": {color: themeColors.color2, type: 'smooth-area'},
        "trend-chart": {color: themeColors.color3, type: 'column'}
    };
    let scheme = [{
        name: "Time",
        type: "date",
        format: "%Y-%m-%d"
    }, {
        name: category,
        type: "number"
    }];

    elem.find('.js-sensor-category').text(category);
    const fusionTable = new FusionCharts.DataStore().createDataTable(getMeasure(category.toLowerCase(), data), scheme);

    elem.find('.chart').insertFusionCharts({
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
                paletteColors: styles[id].color,
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
                "plot": {
                    "value": category,
                    type: styles[id].type,
                    style: {'area': {"fill-opacity": 0.15}}
                },
                "format": {"suffix": data_py.sensor.unit},
                title: ''
            }]
        }
    });
}

function getMeasure(measure, data) {
    let measureData = [];
    for (let i = 0; i < data.length; i++) {
        measureData.push([data[i]['date'], data[i][measure]])
    }
    return measureData
}
