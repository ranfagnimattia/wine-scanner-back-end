class Dashboard {
    constructor(data) {
        this.measure = data.measure;

        this.allData = data.allData;
        this.last = data.last;
        this.lastMonth = data.lastMonth;
        this.diff = data.diff;
        this.monthMean = data.monthMean;
        this.weekMean = data.weekMean;
        this.yesterday = data.yesterday;
        this.sensor = data.sensor;
    }


    update() {
        console.log(this);
        // this.setEvents();
        //
        // const firstMeasure = this.measures[0].toLowerCase();
        // $('.js-main-measure').text(firstMeasure);
        // const animation = new Animation();
        // const lastAnim = [], monthAnim = [];
        // $('[class*="js-show-"]').hide();
        // this.measures.forEach((m) => {
        //     const measure = m.toLowerCase();
        //     $('.js-show-' + measure).show();
        //     lastAnim.push([$('.js-last-' + measure), this.last[measure]]);
        //     monthAnim.push([$('.js-monthMean-' + measure), this.monthMean[measure]]);
        // });
        //
        // animation.setValues(lastAnim, $('.js-last-space'));
        // animation.setValues(monthAnim, $('.js-monthMean-space'));
        // animation.setValues([
        //     setUpTrend($('.js-trend-day'), firstMeasure, this.last, this.yesterday),
        //     setUpTrend($('.js-trend-week'), firstMeasure, this.last, this.weekMean),
        //     setUpTrend($('.js-trend-month'), firstMeasure, this.last, this.monthMean)
        // ], $('.js-trend-space'));
        // animation.animate();
        //
        this.updateCharts();
    }

    setEvents() {
        const $this = this;
        $('#month-chart .btn').off('click').click(function () {
            if (!$(this).hasClass("active"))
                $this.updateChart($('#month-chart'), $this.lastMonth, $(this).data('measure').toLowerCase())
        });
        $('#trend-chart .btn').off('click').click(function () {
            if (!$(this).hasClass("active"))
                $this($('#trend-chart'), $this.diff, $(this).data('measure').toLowerCase())
        });
    }


    /* Charts */
    updateCharts() {
        this.updateBigChart($('#sensor-chart'), this.allData);
        // this.setUpChart($('#month-chart'), this.lastMonth);
        // this.setUpChart($('#trend-chart'), this.diff);
    }

    updateBigChart(elem, data) {

        data = [
            [
                "1901 Jan",
                "Assam",
                127.1,
                150,
                27.1
            ],
            [
                "1901 Feb",
                "Assam",
                119.5,
                150,
                19.5
            ],
            [
                "1901 Mar",
                "Assam",
                130.6,
                150,
                30.6
            ],
            [
                "1901 Apr",
                "Assam",
                1223,
                150,
                223
            ],
            [
                "1901 May",
                "Assam",
                1207,
                150,
                223
            ],
            [
                "1901 Jun",
                "Assam",
                1524.9,
                150,
                524.9
            ]];
        let scheme = [];
        scheme.push({
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        }, {name: 'Min', type: "number"}, {name: 'Max', type: "number"});
        // this.measures.forEach((m) => {
        //     scheme.push({name: m, type: "number"});
        // });
        scheme = [{
            "name": "Time",
            "type": "date",
            "format": "%Y %b"
        },
            {
                "name": "State",
                "type": "string"
            },
            {
                "name": "Rainfall",
                "type": "number"
            },
            {
                "name": "Andrea",
                "type": "number"
            },
            {
                "name": "Altro",
                "type": "number"
            },
        ];

        // $('.js-sensor-measure').text(this.measures.join(', '));
        const fusionTable = new FusionCharts.DataStore().createDataTable(data, scheme);

        // [{
        //                 "value": 'Min',
        //                 type: 'area',
        //                 style: {'area': {"fill-opacity": 0}}
        //             }, {
        //                 "value": 'Max',
        //                 type: 'area',
        //                 style: {'area': {"fill-opacity": 0.15}}
        //             }]
        elem.find('.chart').insertFusionCharts({
            type: 'timeseries',
            width: '100%',
            height: '100%',
            dataFormat: 'json',
            dataSource: {
                chart: {
                    theme: 'candy',
                    paletteColors: '#ffffff, #27293d, #ff293d',
                },
                // series: "State",
                data: fusionTable,
                yAxis: [{
                    "plot": [{
                        value: "Rainfall",
                        type: "area",
                        style: {
                            plot: {
                                "fill-opacity": "0.2"
                            }, "line": {
                                "opacity": 0
                            }
                        }
                    }, {
                        value: "Altro",
                        type: "area",
                        style: {
                            plot: {
                                "fill-opacity": "1"
                            }, "line": {
                                "opacity": 0
                            }
                        }
                    }, {
                        value: "Andrea",
                        type: "line",
                        style: {
                            plot: {
                                "fill-opacity": "1",
                                "color": "#00ff00",
                                "fill": "#00ff00",
                                "fill-color": "#00ff00",
                                stroke: "#003840"
                            }, "line": {
                                "color": "#00ff00",
                                "fill": "#00ff00",
                                "fill-color": "#00ff00",
                                "opacity": 1
                            },
                            stroke: "#003840",
                            "color": "#00ff00",
                            "fill": "#00ff00",
                            "fill-color": "#00ff00",
                        }
                    }],
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
            "trend-chart": {color: themeColors.color3, type: 'column'}
        };
        let scheme = [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        }, {
            name: measure,
            type: "number"
        }];

        elem.find('.js-sensor-measure').text(measure);
        const fusionTable = new FusionCharts.DataStore().createDataTable(getMeasure(measure.toLowerCase(), data), scheme);

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
                        "value": measure,
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