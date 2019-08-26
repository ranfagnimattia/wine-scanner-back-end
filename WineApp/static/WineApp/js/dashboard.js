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
    static TIME = 1;
    static INT = 2;


    constructor(unit) {
        this.animations = [];
        this.unit = '<span class="js-unit">' + unit + '</span>';
    }

    setValues(valuesPair, spaceElem) {
        valuesPair = valuesPair.map((pair) => ({
            elem: pair[0],
            value: (pair[2] === Animation.TIME) ? pair[1].replace(/:/g, "") : pair[1],
            type: pair[2]
        }));

        const widths = valuesPair.map((pair) => spaceElem.html(this._format(pair)).width());
        const maxWidthPair = valuesPair[widths.indexOf(Math.max(...widths))];
        spaceElem.html(this._format(maxWidthPair) + '0');
        this.animations = this.animations.concat(valuesPair);
    }

    _animate() {
        const initValues = {};
        const finalValues = {};
        const $this = this;
        this.animations.forEach((pair, i) => {
            initValues[i] = 0;
            finalValues[i] = pair.value;
        });
        $(initValues).animate(finalValues, {
            duration: 1000,
            easing: 'easeOutQuart',
            step: function () {
                for (let prop in this)
                    if (this.hasOwnProperty(prop)) {
                        const pair = $this.animations[prop];
                        pair.value = this[prop];
                        pair.elem.html($this._format(pair));
                    }
            }
        });
    }

    _format(pair) {
        function formatTime(t) {
            return (t < 10) ? '0' + t : t;
        }

        if (pair.type === Animation.TIME) {
            const h = Math.floor(pair.value / 10000);
            const m = Math.floor((pair.value - h * 10000) / 100);
            const s = Math.floor(pair.value - h * 10000 - m * 100);
            return formatTime(h) + ':' + formatTime(m) + ':' + formatTime(s);
        } else if (pair.type === Animation.INT) {
            return pair.value.toFixed(0);
        } else
            return pair.value.toFixed(2) + this.unit;
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
        if (options.yAxis) {
            options.yAxis.title = '';
            if (options.limits) {
                options.yAxis.min = options.limits.min !== undefined ? options.limits.min : undefined;
                options.yAxis.max = options.limits.max !== undefined ? options.limits.max + 0.1 : undefined;
            }
        }
        this.elem.find('.chart').insertFusionCharts({
            type: 'timeseries',
            width: '100%',
            height: '100%',
            dataFormat: 'json',
            dataSource: {
                tooltip: {
                    outputTimeFormat: {
                        Hour: options.onlyHours ? "%H:00" : "%d %b %Y, %H:00",
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
                        Day: options.onlyHours ? "00" : undefined,
                        Hour: "%H",
                        Minute: "%H:%M",
                        Second: "%H:%M:%S",
                    },
                    initialInterval: options.initialInterval
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
        this.buttons = buttons.slice();
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
    let buttons = Dashboard.initButtons(data_py);
    if (buttons) {
        const btnList = {
            chart1: [],
            chart2: [],
            chart3: [],
            linkedButtons: false
        };
        $.extend(btnList, buttons);
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
    }
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
    if (dashboard['updateButtons'] && buttons)
        dashboard['updateButtons'](buttons);
    const animation = new Animation(data.sensor.unit.replace('^2', '<sup>2</sup>'));
    dashboard.updateCards(animation);
    animation._animate();
    if (buttons) {
        buttons.forEach((btn) => btn.setEvents());
        buttons.forEach((btn) => btn.clickActive());
    }
}