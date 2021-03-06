/**
 * @prop chart1Btn
 * @prop chart2Btn
 * @prop chart3Btn
 */
class Dashboard {
    constructor() {
        $('#navigation a.js-navbar-anomalies').addClass('selected');
    }

    static initButtons(data) {
        return {chart1: data.methods, chart2: data.methods, chart3: ['All'].concat(data.methods), linkedButtons: true};
    }

    update(data) {
        this.sensor = data.sensor;
        this.methods = data.methods;

        this.allData = data.allData;
        this.allDataPrediction = data.allDataPrediction;
        this.allAnomalies = data.allAnomalies;
        this.lastMonth = data.lastMonth;

        this.methodStats = data.methodStats;
        this.anomaliesStats = data.anomaliesStats;

        this.chart3Btn = 'all';

        this.lastMonthScheme = [{
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
            name: 'Error',
            type: "number"
        }];
    }

    updateCards(animation) {
        const methodMonth = [];
        const methodTot = [];
        const methodMse = [];
        this.methods.forEach((method) => {
            const m = method.toLowerCase();
            methodMonth.push([$('.js-' + m + '-month'), this.methodStats[m]['lastMonth'], Animation.INT]);
            methodTot.push([$('.js-' + m + '-tot'), this.methodStats[m]['tot'], Animation.INT]);
            methodMse.push([$('.js-' + m + '-mse'), this.methodStats[m]['mse']]);
        });
        animation.setValues(methodMonth, $('.js-method-month-space'));
        animation.setValues(methodTot, $('.js-method-tot-space'));
        animation.setValues(methodMse, $('.js-method-mse-space'));

        const anomaliesMonth = [];
        const anomaliesTot = [];
        ['minor', 'medium', 'major'].forEach((type) => {
            anomaliesMonth.push([$('.js-' + type + '-month'), this.anomaliesStats['lastMonth'][type], Animation.INT]);
            anomaliesTot.push([$('.js-' + type + '-tot'), this.anomaliesStats['tot'][type], Animation.INT]);
        });
        animation.setValues(anomaliesMonth, $('.js-anomalies-month-space'));
        animation.setValues(anomaliesTot, $('.js-anomalies-tot-space'));
    }


    /* Charts */
    updateChart1(chart) {
        $('.js-chart1-method').text(this.chart1Btn);

        chart.create(this.lastMonth[this.chart1Btn], this.lastMonthScheme, {
            colors: [themeColors.color2, '#25002b', themeColors.color2],
            yAxis: {
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
                }],
                "format": {"suffix": this.sensor.unit}
            },
            limits: this.sensor
        });
    }

    updateChart2(chart) {
        chart.create(this.lastMonth[this.chart2Btn], this.lastMonthScheme, {
            colors: [themeColors.color3],
            yAxis: {
                "plot": [{
                    value: 'Error',
                    type: 'column'
                }]
            }
        });
    }

    updateChart3(chart) {
        const colors = [0, themeColors.color2, themeColors.color3, themeColors.color4];
        if (this.chart3Btn !== 'all') {
            $('.js-chart3-method').text('con il metodo ' + this.chart3Btn);

            chart.create(this.allDataPrediction[this.chart3Btn], this.lastMonthScheme, {
                colors: [themeColors.color1, '#290902', themeColors.color1],
                navigator: true,
                yAxis: {
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
                                "fill-opacity": 0.32
                            }, "line": {
                                "opacity": 0
                            }
                        }
                    }, {
                        value: 'Actual',
                        type: 'smooth-line'
                    }],
                    "format": {"suffix": this.sensor.unit}
                },
                limits: this.sensor
            });
        } else {
            $('.js-chart3-method').text('');
            chart.create(this.allData, [{
                name: "Time",
                type: "date",
                format: "%Y-%m-%d"
            }, {
                name: 'Actual',
                type: "number"
            }], {
                navigator: true,
                yAxis: {
                    "plot": {
                        value: 'Actual'
                    },
                    "format": {"suffix": this.sensor.unit}
                },
                dataMarker: this.allAnomalies.map((d) => ({
                    seriesName: "Actual",
                    time: d.date,
                    identifier: '',
                    timeFormat: "%Y-%m-%d",
                    toolText: d.methods.map((m) =>
                        '<i class="fas fa-caret-' + (m[1] ? 'up' : 'down') + ' pr-1"></i>' + m[0]).join(', '),
                    "style": {
                        "marker": {
                            "fill": colors[d['gravity']]
                        }
                    }
                })),
                limits: this.sensor
            });
        }
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
