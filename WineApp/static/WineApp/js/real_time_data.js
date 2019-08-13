class Dashboard {
    constructor(data) {
        this.chartAll = data.chartAll;
        this.chartLast24h = data.chartLast24h;
        this.chartDiff = data.chartDiff;
        this.lastDayStats = data.lastDayStats;

        // this.measures = data.measures;
        // this.monthMean = data.monthMean;
        // this.weekMean = data.weekMean;
        // this.yesterday = data.yesterday;
        this.sensor = data.sensor;
    }


    update() {
        console.log(this);
        // this.setEvents();

        // const firstMeasure = this.measures[0].toLowerCase();
        // $('.js-main-measure').text(firstMeasure);
        const animation = new Animation();
        const lastAnim = [], monthAnim = [];
        // $('[class*="js-show-"]').hide();
        // this.measures.forEach((m) => {
        //     const measure = m.toLowerCase();
        //     $('.js-show-' + measure).show();
        //     lastAnim.push([$('.js-last-' + measure), this.last[measure]]);
        //     monthAnim.push([$('.js-monthMean-' + measure), this.monthMean[measure]]);
        // });


        $('.js-lastDay-maxTime').text(this.lastDayStats.maxTime);
        $('.js-lastDay-minTime').text(this.lastDayStats.minTime);
        animation.setValues([
            [$('.js-lastDay-max'), this.lastDayStats.max],
            [$('.js-lastDay-min'), this.lastDayStats.min]
        ], $('.js-lastDay-space'));

        // animation.setValues(monthAnim, $('.js-monthMean-space'));
        // animation.setValues([
        //     setUpTrend($('.js-trend-day'), firstMeasure, this.last, this.yesterday),
        //     setUpTrend($('.js-trend-week'), firstMeasure, this.last, this.weekMean),
        //     setUpTrend($('.js-trend-month'), firstMeasure, this.last, this.monthMean)
        // ], $('.js-trend-space'));
        animation.animate();

        this.updateCharts();
    }

    setEvents() {
        const $this = this;
        $('#month-chart .btn').off('click').click(function () {
            if (!$(this).hasClass("active"))
                $this.updateChart($('#month-chart'), $this.chartLast24h, $(this).data('measure').toLowerCase())
        });
        $('#trend-chart .btn').off('click').click(function () {
            if (!$(this).hasClass("active"))
                $this($('#trend-chart'), $this.chartDiff, $(this).data('measure').toLowerCase())
        });
    }


    /* Charts */
    updateCharts() {
        this.updateBigChart($('#sensor-chart'), this.chartAll);
        this.updateChart($('#month-chart'), this.chartLast24h, "%Y-%m-%d %H:%M:%S");
        this.updateChart($('#trend-chart'), this.chartDiff, "%Y-%m-%d %H");
    }

    updateBigChart(elem, data) {
        let scheme = [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d %H:%M:%S"
        }, {
            name: 'Rilevazione',
            type: "number"
        }];

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
                    "plot": {
                        value: 'Rilevazione',
                        connectnulldata: true
                    },
                    "format": {"suffix": this.sensor.unit},
                    title: ''
                }]
            }
        });
    }

    setUpChart(elem, data) {
        elem.find('.btn').attr("disabled", "disabled");
        this.measures.forEach((m, i) => {
            const btn = elem.find(`[data-measure='${m}']`);
            btn.removeAttr("disabled");
            if (i === 0) {
                btn.addClass("active");
                this.updateChart(elem, data, m);
            }
        });
    }

    updateChart(elem, data, timeFormat) {
        let id = elem.attr('id');
        let styles = {
            "month-chart": {color: themeColors.color2, type: 'smooth-area'},
            "trend-chart": {color: themeColors.color3, type: 'column'}
        };
        let scheme = [{
            name: "Time",
            type: "date",
            format: timeFormat
        }, {
            name: 'Rilevazione',
            type: "number"
        }];

        // elem.find('.js-sensor-measure').text(measure);
        const fusionTable = new FusionCharts.DataStore().createDataTable(data, scheme);

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
                        "value": 'Rilevazione',
                        connectnulldata: true,
                        type: styles[id].type,
                        style: {'area': {"fill-opacity": 0.15}}
                    },
                    "format": {"suffix": this.sensor.unit},
                    title: ''
                }]
            }
        });
    }
}