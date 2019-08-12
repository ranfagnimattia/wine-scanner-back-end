/**
 * @param data_py.getUrl
 * @param data_py.updateUrl
 *
 * @param response.updated
 * @param response.created
 */

// Utilities
class Animation {
    animations = [];

    static _getTextWidth(elem, text) {
        return elem.text(text).width()
    }

    setValues(valuesPair, spaceElem) {
        const widths = valuesPair.map((pair) => Animation._getTextWidth(spaceElem, pair[1].toFixed(2)));
        spaceElem.text(valuesPair[widths.indexOf(Math.max(...widths))][1].toFixed(2) + '0');
        this.animations = this.animations.concat(valuesPair);
    }

    animate() {
        const initValues = {};
        const elements = {};
        const finalValues = {};
        this.animations.forEach((pair, i) => {
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
});

function _updateData() {
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

                $('.nav-item.active .nav-sensor').click();
                $('.nav-item.active .nav-measures li.active .nav-measure').click();
            });

        }, error: function (response) {
            console.error(response);
        }
    });
}

function _updateDashboard(data) {
    $('.active').removeClass("active");
    $(`.nav-sensor[data-id='${data.sensor.id}']`).parent().addClass("active");
    const sensorToggle = $(`.nav-sensor-toggle[data-id='${data.sensor.id}']`);
    sensorToggle.next('.nav-measures').find(`.nav-measure[data-measure='${data.measure}']`).parent().addClass("active");
    sensorToggle.parent().addClass("active");

    const refreshElem = $('#refresh');
    if (refreshElem.hasClass('link')) {
        refreshElem.html('<i class="fas fa-check"></i> <span>Tutti i dati sono aggiornati</span>')
            .removeClass('link').off('click');
    }

    // Common classes
    $('.js-sensor').text(data.sensor.name);
    $('.js-sensor-icon').html('<i class="' + data.sensor.icon + '"></i>');
    $('.js-unit').html(data.sensor.unit.replace('^2', '<sup>2</sup>'));

    $('.js-measure').text(data.measure);

    new Dashboard(data).update();
}
