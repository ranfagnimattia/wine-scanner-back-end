let activeDiffBtn = 'avg';

/**
 * @param data.lastDayStats.maxTime
 * @param data.lastDayStats.minTime
 * @param data.trend.lastDay
 */
class Dashboard {
    constructor(data) {
        this.sensor = data.sensor;
        // this.measure = data.measure;

        this.chartAll = data.chartAll;
        this.anomaliesAll = data.anomaliesAll;
        this.chartLastMonth = data.chartLastMonth;

        // this.chartDiff = data.chartDiff;
        //
        // this.last = data.last;
        // this.lastTime = data.lastTime;
        // this.lastDayStats = data.lastDayStats;
        // this.trend = data.trend;
    }


    update() {
        console.log(this);
        // this.setEvents();
        //
        // $('.js-main-measure').text(this.mainMeasure);
        //
        // const animation = new Animation();
        // animation.setValues([
        //     [$('.js-last-value'), this.last],
        //     [$('.js-last-time'), this.lastTime, true],
        //     [$('.js-lastDay-mainMeasure'), this.lastDayStats[this.mainMeasure]]
        // ], $('.js-last-space'));
        // animation.setValues([
        //     [$('.js-lastDay-max'), this.lastDayStats.max],
        //     [$('.js-lastDay-maxTime'), this.lastDayStats.maxTime, true],
        //     [$('.js-lastDay-min'), this.lastDayStats.min],
        //     [$('.js-lastDay-minTime'), this.lastDayStats.minTime, true]
        // ], $('.js-lastDay-space'));
        // animation.setValues([
        //     setUpTrend($('.js-trend-previous'), this.trend.previous),
        //     setUpTrend($('.js-trend-lastDay'), this.trend.lastDay),
        // ], $('.js-trend-space'));
        // animation.animate();
        //
        this.updateCharts();
    }

    setEvents() {
        const $this = this;
        $('#diff-chart .btn').off('click').click(function () {
            if (!$(this).hasClass('active')) {
                $(this).addClass('js-active');
                const elem = $('#diff-chart');
                activeDiffBtn = $(this).data('type');
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
                $this.updateChart(elem, $this.chartDiff[activeDiffBtn], "%Y-%m-%d %H", title);
            }
        });
    }


    /* Charts */
    updateCharts() {
        this.updateBigChart($('#sensor-chart'), this.chartAll);
        this.updateMonthChart();
        this.updateBarChart();
        // $('#diff-chart .btn[data-type=\'' + activeDiffBtn + '\']').click();
    }

    updateBigChart(elem, data) {
        let scheme = [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        }, {
            name: 'Actual',
            type: "number"
        }];

        const dataMarker = this.anomaliesAll.map((d) => ({
            seriesname: "Actual",
            time: d[0],
            identifier: "H",
            timeformat: "%Y-%m-%d",
            tooltext: "he ral fund rates to approach 20 percent."
        }));

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
                        value: 'Actual'
                    },
                    "format": {"suffix": this.sensor.unit},
                    title: ''
                }],
                datamarker: dataMarker
            }
        });
    }

    updateMonthChart() {
        const elem = $('#month-chart');
        let scheme = [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        }, {
            name: 'Actual',
            type: "number"
        }, {
            name: 'Prediction',
            type: "number"
        }, {
            name: 'Upper limit',
            type: "number"
        }, {
            name: 'Lower limit',
            type: "number"
        }];

        const fusionTable = new FusionCharts.DataStore().createDataTable(this.chartLastMonth, scheme);

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
                    paletteColors: themeColors.color2 + ',' + '#25002b' +
                        themeColors.color3 + ',' + themeColors.color2 + ',',
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
                    "plot": [{
                        value: 'Upper limit',
                        type: 'smooth-area',
                        style: {
                            plot: {
                                "fill-opacity": 0.15
                            }, "line": {
                                "opacity": 0
                            }
                        }
                    }, {
                        value: 'Lower limit',
                        type: 'smooth-area',
                        style: {
                            plot: {
                                "fill-opacity": 0.38
                            }, "line": {
                                "opacity": 0
                            }
                        }
                    }, {
                        value: 'Actual',
                        type: 'smooth-line'
                    },
                        // {
                        //     value: 'Prediction',
                        //     type: 'smooth-line'
                        // }
                    ],
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

    updateBarChart() {
        const elem = $('#diff-chart');
        let scheme = [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        }, {
            name: 'Actual',
            type: "number"
        }, {
            name: 'Prediction',
            type: "number"
        }, {
            name: 'Upper limit',
            type: "number"
        }, {
            name: 'Lower limit',
            type: "number"
        }, {
            name: 'Anomalies',
            type: "number"
        }];

        const fusionTable = new FusionCharts.DataStore().createDataTable(this.chartLastMonth, scheme);

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
                    paletteColors: themeColors.color3,
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
                    "plot": [{
                        value: 'Anomalies',
                        type: 'column'
                    }],
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


/*
RGB3: final color
RGB2: background
A1: alpha of RGB1
RGB1: foreground color

r3=39, g3=41, b3=61
r2=40, g2=66, b2=72
a1=0.38
r1 = (r3 - r2 + r2*a1)/a1
g1 = (g3 - g2 + g2*a1)/a1
b1 = (b3 - b2 + b2*a1)/a1
'R:'+r1+' G:'+g1+ ' B:'+b1
 */