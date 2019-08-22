/**
 * @param data_py.getUrl
 * @param data_py.updateUrl
 * @param data_py.lastUpdate
 * @param data_py.autoUpdate
 *
 * @param response.updated
 * @param response.created
 */

// Utilities
class Animation {
    animations = [];

    setValues(valuesPair, spaceElem) {
        function getTextWidth(elem, text) {
            return elem.text(text).width()
        }

        const widths = valuesPair.map((pair) => pair[2] !== true ?
            getTextWidth(spaceElem, pair[1].toFixed(2)) : 0);
        spaceElem.text(valuesPair[widths.indexOf(Math.max(...widths))][1].toFixed(2) + '0');
        this.animations = this.animations.concat(valuesPair);
    }

    _animate() {
        function formatTime(t) {
            return (t < 10) ? '0' + t : t;
        }

        const initValues = {};
        const elements = {};
        const timeValues = {};
        const finalValues = {};
        this.animations.forEach((pair, i) => {
            initValues[i] = 0;
            elements[i] = pair[0];
            timeValues[i] = pair[2] === true;
            finalValues[i] = pair[2] === true ? pair[1].replace(/:/g, "") : pair[1];
        });
        $(initValues).animate(finalValues, {
            duration: 1000,
            easing: 'easeOutQuart',
            step: function () {
                for (let prop in this)
                    if (this.hasOwnProperty(prop)) {
                        if (timeValues[prop]) {
                            const h = Math.floor(this[prop] / 10000);
                            const m = Math.floor((this[prop] - h * 10000) / 100);
                            const s = Math.floor(this[prop] - h * 10000 - m * 100);
                            elements[prop].text(formatTime(h) + ':' + formatTime(m) + ':' + formatTime(s));
                        } else
                            elements[prop].text(this[prop].toFixed(2));
                    }
            }
        });
    }
}


class Chart {
    constructor(elem) {
        this.elem = elem;
    }

    setTitle(title) {
        this.elem.find('.card-title').text(title);
    }

    setCategory(category) {
        this.elem.find('.card-category').text(category);
    }

    create(data, scheme, options) {
        const fusionTable = new FusionCharts.DataStore().createDataTable(data, scheme);
        const enabled = options && options.navigator ? '1' : '0';
        this.elem.find('.chart').insertFusionCharts({
            type: 'timeseries',
            width: '100%',
            height: '100%',
            dataFormat: 'json',
            dataSource: {
                tooltip: {
                    outputTimeFormat: {
                        Hour: "%d %b %Y, %H:00",
                        Minute: "%d %b %Y, %H:%M",
                        Second: "%d %b %Y, %H:%M:%S",
                    }
                },
                navigator: {
                    enabled: enabled,
                },
                chart: {
                    theme: 'candy',
                    paletteColors: options && options.colors ? options.colors.join(',') : undefined,
                    "showLegend": enabled
                },
                "extensions": {
                    "standardRangeSelector": {
                        "enabled": enabled
                    },
                    "customRangeSelector": {
                        "enabled": enabled
                    }
                },
                data: fusionTable,
                yAxis: options ? options.yAxis : undefined,
                xAxis: {
                    outputTimeFormat: {
                        Hour: "%H",
                        Minute: "%H:%M",
                        Second: "%H:%M:%S",
                    }
                },
                dataMarker: options && options.dataMarker ? options.dataMarker : []
            }
        });
    }


}


class Button {
    constructor(key, buttons, dashboard) {
        this.elem = $('#' + key);
        this.update = 'update' + ucFirst(key);
        this.buttons = buttons;
        this.attr = key + 'Btn';
        this.chart = new Chart(this.elem);
        this.dashboard = dashboard;

        if (this.buttons.length === 0)
            return;

        let html = '';
        const color = key === 'chart1' ? '2' : '3';
        this.buttons.forEach((btn, i) => {
            if (typeof btn === 'string' || btn instanceof String)
                this.buttons[i] = {name: btn};

            btn = this.buttons[i];
            if (!btn.value || btn.value === '')
                btn.value = btn.name.toLowerCase();
            html +=
                '<label class="btn btn-sm btn-color' + color + ' btn-simple" data-value="' + btn.value + '">' +
                '   <input type="radio" class="d-none d-sm-none" name="options">' +
                '   <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">' + btn.name + '</span>' +
                '   <span class="d-block d-sm-none">' + btn.name + '</span>' +
                '</label>';
        });
        this.elem.find('.card-header>div.row').append('<div class="col-sm-6">' +
            '<div class="btn-group btn-group-toggle float-right" data-toggle="buttons">' + html + '</div></div>');
    }

    setEvents() {
        if (this.buttons.length === 0)
            return;
        const $this = this;
        this.elem.find('.btn').off('click').click(function () {
            if (!$(this).hasClass('active')) {
                $this.dashboard[$this.attr] = $(this).data('value');
                $this.dashboard[$this.update]($this.chart);
                if ($this.linkedBtn && !$this.linkedClick) {
                    $this.linkedBtn._linkedClicked($this.dashboard[$this.attr]);
                }
            }
        });
    }

    clickActive() {
        if (this.buttons.length === 0)
            return this.dashboard[this.update](this.chart);
        if (!this.dashboard[this.attr])
            this.dashboard[this.attr] = this.buttons[0].value;
        this.elem.find('.btn[data-value="' + this.dashboard[this.attr] + '"]').click();
    }

    setLinked(btn) {
        this.linkedBtn = btn;
    }

    _linkedClicked(value) {
        this.dashboard[this.attr] = value;
        this.linkedClick = true;
        this.clickActive();
        this.linkedClick = false;
    }

    disableOthers(values) {
        this.elem.find('.btn').attr("disabled", "disabled");
        values.forEach((v, i) => {
            const btn = this.elem.find(`[data-value='${v.toLowerCase()}']`);
            btn.removeAttr("disabled");
            if (i === 0 && values.indexOf(this.dashboard[this.attr]) < 0) {
                this.dashboard[this.attr] = v.toLowerCase();
            }
        });
    }

}


function setUpTrend(elem, trend) {
    if (trend > 0)
        elem.find('.js-trend-icon').html('<i class="fas fa-caret-up"></i>');
    else if (trend < 0)
        elem.find('.js-trend-icon').html('<i class="fas fa-caret-down"></i>');
    else
        elem.find('.js-trend-icon').html('<i class="fas fa-minus"></i>');

    return [elem.find('.js-trend'), trend]
}

function ucFirst(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}


function getMeasure(measure, data) {
    let measureData = [];
    for (let i = 0; i < data.length; i++) {
        measureData.push([data[i]['date'], data[i][measure]])
    }
    return measureData
}

// Dashboard
$('document').ready(function () {
    const dashboard = new Dashboard();
    const btnList = {
        chart1: [],
        chart2: [],
        chart3: [],
        linkedButtons: false
    };
    $.extend(btnList, Dashboard.initButtons(data_py));
    let buttons;
    if (btnList.linkedButtons) {
        const c1 = new Button('chart1', btnList['chart1'], dashboard);
        const c2 = new Button('chart2', btnList['chart2'], dashboard);
        c1.setLinked(c2);
        c2.setLinked(c1);
        buttons = [c1, c2, new Button('chart3', btnList['chart3'], dashboard)];
    } else
        buttons = [new Button('chart1', btnList['chart1'], dashboard),
            new Button('chart2', btnList['chart2'], dashboard),
            new Button('chart3', btnList['chart3'], dashboard)];
    _updateDashboard(data_py, dashboard, buttons);

    // Sidebar
    $('.nav-sensor:not([disabled])').click(function () {
        if (data_py.getUrl)
            $.getJSON({
                url: data_py.getUrl,
                data: {
                    'sensorId': $(this).data('id')
                },
                success: function (response) {
                    if (response) {
                        _updateDashboard(response, dashboard, buttons);
                    }
                }, error: function (response) {
                    console.error(response);
                }
            });
    });

    $('.nav-measure').click(function () {
        if (data_py.getUrl)
            $.getJSON({
                url: data_py.getUrl,
                data: {
                    'sensorId': $(this).parents('.nav-measures').prev('.nav-sensor-toggle').data('id'),
                    'measure': $(this).data('measure')
                },
                success: function (response) {
                    if (response) {
                        _updateDashboard(response, dashboard, buttons);
                    }
                }, error: function (response) {
                    console.error(response);
                }
            });
    });

    $('.nav-sensor-toggle:not([disabled])').click(function () {
        $(this).find('.caret-icon').toggleClass('fa-rotate-180');
        $(this).next('.nav-measures').slideToggle();
    });

    _updateData();
    if (data_py.autoUpdate)
        setInterval(_updateData, 60000);
});

let created = 0;

function _updateData() {
    const elem = $('#refresh');
    elem.html('<i class="fas fa-redo fa-spin"></i> <span>Aggiornamento...</span>').removeClass('link').off('click');

    $.getJSON({
        url: data_py.updateUrl,
        success: function (response) {
            if (!response || response.error) {
                elem.html('<i class="fas fa-times"></i><span>' +
                    (!response ? 'Errore server' : response.error) + '</span>');
                return;
            }
            created += response.created ? response.created : 0;
            if (!response.updated && created === 0) {
                elem.html('<i class="fas fa-check"></i> <span>Tutti i dati sono aggiornati</span>');
                return;
            }
            let msg = 'Ricarica ora ';
            if (response.updated > 0)
                msg += response.updated + ' dati aggiornati';
            if (created > 0) {
                if (response.updated > 0)
                    msg += ' e ';
                msg += created + ' nuovi dati';
            }
            elem.html('<i class="fas fa-redo"></i> <span>' + msg + '</span>').addClass('link').click(() => {
                $('.nav-item.active .nav-sensor').click();
                $('.nav-item.active .nav-measures li.active .nav-measure').click();
            });

        }, error: function (response) {
            console.error(response);
            elem.html('<i class="fas fa-times"></i><span>Errore connessione</span>');
        }
    });
}

function _updateDashboard(data, dashboard, buttons) {
    $('.active').removeClass('active');
    $(`.nav-sensor[data-id='${data.sensor.id}']`).parent().addClass('active');
    const sensorToggle = $(`.nav-sensor-toggle[data-id='${data.sensor.id}']`);
    sensorToggle.next('.nav-measures').find(`.nav-measure[data-measure='${data.measure}']`).parent().addClass('active');
    sensorToggle.parent().addClass('active');

    const refreshElem = $('#refresh');
    if (refreshElem.hasClass('link')) {
        created = 0;
        refreshElem.html('<i class="fas fa-check"></i> <span>Tutti i dati sono aggiornati</span>')
            .removeClass('link').off('click');
    }

    // Common classes
    $('.js-last-update').text(data.lastUpdate.date + ' alle ' + data.lastUpdate.time);
    $('.js-last-date').text(data.lastUpdate.date);

    $('.js-sensor').text(data.sensor.name);
    $('.js-sensor-icon').html('<i class="' + data.sensor.icon + '"></i>');
    $('.js-unit').html(data.sensor.unit.replace('^2', '<sup>2</sup>'));

    $('.js-measure').text(data.measure);

    if (data.error)
        return console.error(data.error);

    dashboard.update(data);
    console.log(dashboard);
    if (dashboard['updateButtons'])
        dashboard['updateButtons'](buttons);
    const animation = new Animation();
    dashboard.updateCards(animation);
    animation._animate();
    buttons.forEach((btn) => btn.setEvents());
    buttons.forEach((btn) => btn.clickActive());
}