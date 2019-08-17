class Dashboard {
    constructor(data) {
        this.sensor = data.sensor;
        this.measures = data.measures;

        this.chartAll = data.chartAll;
        this.chartLastMonth = data.chartLastMonth;
        this.chartDiff = data.chartDiff;

        this.last = data.last;
        this.lastMonthStats = data.lastMonthStats;
        this.trend = data.trend;
    }


    update() {
        console.log(this);
        this.setEvents();

        $('.js-main-measure').text(this.measures[0]);
        const animation = new Animation();
        const lastAnim = [], monthAnim = [];
        $('[class*="js-show-"]').hide();
        this.measures.forEach((m) => {
            $('.js-show-' + m).show();
            lastAnim.push([$('.js-last-' + m), this.last[m]]);
            monthAnim.push([$('.js-lastMonthStats-' + m), this.lastMonthStats[m]]);
        });

        animation.setValues(lastAnim, $('.js-last-space'));
        animation.setValues(monthAnim, $('.js-lastMonthStats-space'));
        animation.setValues([
            setUpTrend($('.js-trend-day'), this.trend.day),
            setUpTrend($('.js-trend-week'), this.trend.week),
            setUpTrend($('.js-trend-month'), this.trend.month)
        ], $('.js-trend-space'));
        animation.animate();

        this.updateCharts();
    }

    setEvents() {
        const $this = this;
        $('#month-chart .btn').off('click').click(function () {
            if (!$(this).hasClass("active"))
                $this.updateChart($('#month-chart'), $this.chartLastMonth, $(this).data('measure'))
        });
        $('#diff-chart .btn').off('click').click(function () {
            if (!$(this).hasClass("active"))
                $this.updateChart($('#diff-chart'), $this.chartDiff, $(this).data('measure'))
        });
    }


    /* Charts */
    updateCharts() {
        this.updateBigChart($('#sensor-chart'), this.chartAll);
        this.setUpChart($('#month-chart'), this.chartLastMonth);
        this.setUpChart($('#diff-chart'), this.chartDiff);
    }

    updateBigChart(elem, data) {
        let scheme = [];
        scheme.push({
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        });
        this.measures.forEach((m) => {
            scheme.push({name: ucFirst(m), type: "number"});
        });

        $('.js-sensor-measure').text(this.measures.join(', '));
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
                    "plot": this.measures.map((m) => ({value: ucFirst(m)})),
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

    updateChart(elem, data, measure) {
        let id = elem.attr('id');
        let styles = {
            "month-chart": {color: themeColors.color2, type: 'smooth-area'},
            "diff-chart": {color: themeColors.color3, type: 'column'}
        };
        let scheme = [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        }, {
            name: ucFirst(measure),
            type: "number"
        }];

        elem.find('.js-sensor-measure').text(measure);
        const fusionTable = new FusionCharts.DataStore().createDataTable(getMeasure(measure, data), scheme);

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
                        "value": ucFirst(measure),
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