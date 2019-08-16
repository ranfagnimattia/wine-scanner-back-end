let activeDiffBtn = 'avg';

/**
 * @param data.lastDayStats.maxTime
 * @param data.lastDayStats.minTime
 * @param data.trend.lastDay
 */
class Dashboard {
    constructor(data) {
        this.sensor = data.sensor;

        this.chartAll = data.chartAll;
        this.chartLast24h = data.chartLast24h;
        this.chartDiff = data.chartDiff;

        this.mainMeasure = data.mainMeasure;
        this.last = data.last;
        this.lastTime = data.lastTime;
        this.lastDayStats = data.lastDayStats;
        this.trend = data.trend;
    }


    update() {
        console.log(this);
        this.setEvents();

        $('.js-main-measure').text(this.mainMeasure);

        const animation = new Animation();
        animation.setValues([
            [$('.js-last-value'), this.last],
            [$('.js-last-time'), this.lastTime, true],
            [$('.js-lastDay-mainMeasure'), this.lastDayStats[this.mainMeasure]]
        ], $('.js-last-space'));
        animation.setValues([
            [$('.js-lastDay-max'), this.lastDayStats.max],
            [$('.js-lastDay-maxTime'), this.lastDayStats.maxTime, true],
            [$('.js-lastDay-min'), this.lastDayStats.min],
            [$('.js-lastDay-minTime'), this.lastDayStats.minTime, true]
        ], $('.js-lastDay-space'));
        animation.setValues([
            setUpTrend($('.js-trend-previous'), this.trend.previous),
            setUpTrend($('.js-trend-lastDay'), this.trend.lastDay),
        ], $('.js-trend-space'));
        animation.animate();

        this.updateCharts();
    }

    setEvents() {
        const $this = this;
        $('#diff-chart .btn').off('click').click(function () {
            if (!$(this).hasClass('active')) {
                $(this).addClass('js-active');
                const elem = $('#diff-chart');
                activeDiffBtn = $(this).data('type');
                $this.updateChart(elem, $this.chartDiff[activeDiffBtn], "%Y-%m-%d %H");
                let title, text;
                if (activeDiffBtn === 'avg') {
                    title = 'Media';
                    text = 'Media ' + $this.sensor.name + ' ultima settimana per fascia oraria';
                } else {
                    title = 'Differenza';
                    text = $this.sensor.name + ' rispetto all\'ultima settimana per fascia oraria';
                }

                elem.find('.card-title').text(title);
                elem.find('.card-category').text(text);
            }
        });
    }


    /* Charts */
    updateCharts() {
        this.updateBigChart($('#sensor-chart'), this.chartAll);
        this.updateChart($('#last24h-chart'), this.chartLast24h, "%Y-%m-%d %H:%M:%S");
        $('#diff-chart .btn[data-type=\'' + activeDiffBtn + '\']').click();
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
                tooltip: {
                    outputTimeFormat: {
                        Hour: "%d %b %Y, %H:00",
                        Minute: "%d %b %Y, %H:%M",
                        Second: "%d %b %Y, %H:%M:%S",
                    }
                },
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
                }],
                xAxis: {
                    outputTimeFormat: {
                        Hour: "%H",
                        Minute: "%H:%M",
                        Second: "%H:%M:%S",
                    }
                }
            }
        });
    }

    updateChart(elem, data, timeFormat) {
        let id = elem.attr('id');
        let styles = {
            "last24h-chart": {color: themeColors.color2, type: 'smooth-area'},
            "diff-chart": {color: themeColors.color3, type: 'column'}
        };
        let scheme = [{
            name: "Time",
            type: "date",
            format: timeFormat
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
                tooltip: {
                    outputTimeFormat: {
                        Hour: "%d %b %Y, %H:00",
                        Minute: "%d %b %Y, %H:%M",
                        Second: "%d %b %Y, %H:%M:%S",
                    }
                },
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
                }],
                xAxis: {
                    outputTimeFormat: {
                        Hour: "%H",
                        Minute: "%H:%M",
                        Second: "%H:%M:%S",
                    }
                }
            }
        });
    }
}