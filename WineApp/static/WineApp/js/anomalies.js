/**
 * @prop chart1Btn
 * @prop chart2Btn
 * @prop chart3Btn
 */
class Dashboard {
    static initButtons(data) {
        return {chart1: data.methods, chart2: data.methods, linkedButtons: true};
    }

    update(data) {
        this.sensor = data.sensor;
        this.methods = data.methods;

        this.allData = data.allData;
        this.allAnomalies = data.allAnomalies;
        this.lastMonth = data.lastMonth;

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
    }


    /* Charts */
    updateChart1(chart) {
        $('.js-chart1-method').text(this.chart1Btn);

        chart.create(this.lastMonth[this.chart1Btn], this.lastMonthScheme, {
            colors: [themeColors.color2, '#25002b', themeColors.color2, themeColors.color3],
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
            }]
        });
    }

    updateChart2(chart) {
        chart.create(this.lastMonth[this.chart2Btn], this.lastMonthScheme, {
            colors: [themeColors.color3],
            yAxis: [{
                "plot": [{
                    value: 'Error',
                    type: 'column'
                }],
                title: ''
            }]
        });
    }

    updateChart3(chart) {
        const colors = [0, themeColors.color2, themeColors.color3, themeColors.color4];
        chart.create(this.allData, [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        }, {
            name: 'Actual',
            type: "number"
        }], {
            navigator: true,
            yAxis: [{
                "plot": {
                    value: 'Actual'
                },
                "format": {"suffix": this.sensor.unit},
                title: ''
            }],
            dataMarker: this.allAnomalies.map((d) => ({
                seriesName: "Actual",
                time: d[0],
                // identifier: '' + d[1],
                identifier: '',
                timeFormat: "%Y-%m-%d",
                toolText: d[2],
                "style": {
                    "marker": {
                        "fill": colors[d[1]]
                    }
                }
            })),
            initialInterval: {
                from: this.lastMonth[this.chart1Btn][0][0],
                to: this.lastMonth[this.chart1Btn][this.lastMonth[this.chart1Btn].length - 1][0]
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