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

    animate() {
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
    _updateDashboard(data_py);

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
                        _updateDashboard(response);
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
                        _updateDashboard(response);
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

function _updateDashboard(data) {
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

    new Dashboard(data).update();
}
