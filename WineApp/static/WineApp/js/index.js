class Dashboard {
    constructor() {
        Popper.Defaults.modifiers.computeStyle.gpuAcceleration = !(window.devicePixelRatio < 1.5 && /Win/.test(navigator.platform));
        $('#navigation a.selected').removeClass('selected');
        var selected = $('#navigation a.js-navbar-home');
        selected.removeClass('notselected');
        selected.addClass('selected');


        const $this = this;
        var calendar = $('#calendar').fullCalendar({
            header: {
                left: 'title',
                right: 'prev,next today'
            },
            monthNames: ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre',
                'Ottobre', 'Novembre', 'Dicembre'],
            dayNamesShort: ['Dom', 'Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab'],
            editable: false,
            firstDay: 1,
            selectable: false,
            defaultView: 'month',
            renderViewEvent: function (month, year, monthName) {
                $('.js-calendar-month').text(monthName + ' ' + year);
                $('.js-calendar-year').text(year);

                const empty = {
                    minor: 0, medium: 0, major: 0, tot: 0, min: 0, max: 0, avg: 0
                };
                const monthAnomalies = $this.anomaliesMonth.find((m) => m.date === year + '-' + month) || empty;
                const yearAnomalies = $this.anomaliesYear.find((m) => m.date === year) || empty;
                const monthData = $this.dataMonth.find((m) => m.date === year + '-' + month);
                const measuresMonthAnomalies = $this.anomaliesMeasures.find((m) => m.date === year + '-' + month) || empty;
                const measuresYearAnomalies = $this.anomaliesMeasuresYear.find((m) => m.date === year) || empty;

                const animation = new Animation($this.sensor.unit.replace('^2', '<sup>2</sup>'));

                const anomaliesMonth = [];
                const anomaliesYear = [];
                ['minor', 'medium', 'major'].forEach((type) => {
                    anomaliesMonth.push([$('.js-' + type + '-month'), monthAnomalies[type], Animation.INT]);
                    anomaliesYear.push([$('.js-' + type + '-year'), yearAnomalies[type], Animation.INT]);
                });
                animation.setValues(anomaliesMonth, $('.js-anomalies-month-space'));
                animation.setValues(anomaliesYear, $('.js-anomalies-year-space'));

                if (!$this.measures) {
                    $('.js-monthStats-hide, .js-monthAnomalies-hide').hide();
                    $('.js-monthStats-info, .js-monthAnomalies-info').show().text('Selezionare un sensore');
                } else if (!monthData) {
                    $('.js-monthStats-hide').hide();
                    $('.js-monthStats-info').show().text('Dati non disponibili');
                } else {
                    $('.js-monthStats-info').hide();
                    $('.js-monthStats-hide').show();
                    const monthAnim = [];
                    $this.measures.forEach((m) => {
                        monthAnim.push([$('.js-lastMonthStats-' + m), monthData[m]]);
                    });
                    animation.setValues(monthAnim, $('.js-lastMonthStats-space'));
                }

                $('[class*="js-show-"]').hide();
                if ($this.measures) {
                    $('.js-monthAnomalies-info').hide();
                    $('.js-monthAnomalies-hide').show();
                    const measuresAnimMonth = [];
                    const measuresAnimYear = [];
                    $this.measures.forEach((m) => {
                        $('.js-show-' + m).show();
                        measuresAnimMonth.push([$('.js-monthAnomalies-' + m), measuresMonthAnomalies[m], Animation.INT]);
                        measuresAnimYear.push([$('.js-yearAnomalies-' + m), measuresYearAnomalies[m], Animation.INT]);
                    });
                    animation.setValues(measuresAnimMonth, $('.js-monthAnomalies-space'));
                    animation.setValues(measuresAnimYear, $('.js-yearAnomalies-space'));
                }

                animation._animate();
            }
        });
    }

    update(data) {
        this.sensor = data.sensor;
        this.measures = data.measures;

        this.allAnomalies = data.allAnomalies;
        this.anomaliesMonth = data.anomaliesMonth;
        this.anomaliesYear = data.anomaliesYear;
        this.anomaliesMeasures = data.anomaliesMeasures;
        this.anomaliesMeasuresYear = data.anomaliesMeasuresYear;

        this.dataMonth = data.dataMonth;
    }

    updateCards(animation) {
        $('#calendar').updateFullCalendar(this.allAnomalies);

        // const methodMonth = [];
        // const methodTot = [];
        // const methodMse = [];
        // this.methods.forEach((method) => {
        //     const m = method.toLowerCase();
        //     methodMonth.push([$('.js-' + m + '-month'), this.methodStats[m]['lastMonth'], Animation.INT]);
        //     methodTot.push([$('.js-' + m + '-tot'), this.methodStats[m]['tot'], Animation.INT]);
        //     methodMse.push([$('.js-' + m + '-mse'), this.methodStats[m]['mse']]);
        // });
        // animation.setValues(methodMonth, $('.js-method-month-space'));
        // animation.setValues(methodTot, $('.js-method-tot-space'));
        // animation.setValues(methodMse, $('.js-method-mse-space'));
    }
}
