class Dashboard {
    static initButtons() {
        return {chart1: ['Tot', 'Avg', 'Max', 'Min'], chart2: ['Tot', 'Avg', 'Max', 'Min'], linkedButtons: true};
    }

    update(data) {
        this.sensor = data.sensor;
        this.measures = data.measures;

        this.allData = data.allData;
        this.lastMonth = data.lastMonth;
        this.diff = data.diff;

        this.last = data.last;
        this.lastMonthStats = data.lastMonthStats;
        this.trend = data.trend;
    }

    updateButtons(buttons) {
        buttons[0].disableOthers(this.measures);
        buttons[1].disableOthers(this.measures);
    }

    updateCards(animation) {
        $('.js-main-measure').text(this.measures[0]);
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
    }

    /* Charts */
    updateChart1(chart) {
        chart.elem.find('.js-sensor-measure').text(this.chart1Btn);

        chart.create(getMeasure(this.chart1Btn, this.lastMonth), [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        }, {
            name: ucFirst(this.chart1Btn),
            type: "number"
        }], {
            colors: [themeColors.color2],
            yAxis: [{
                "plot": {
                    "value": ucFirst(this.chart1Btn),
                    type: 'smooth-area',
                    style: {'area': {"fill-opacity": 0.15}}
                },
                "format": {"suffix": this.sensor.unit},
                title: ''
            }]
        });
    }

    updateChart2(chart) {
        chart.elem.find('.js-sensor-measure').text(this.chart2Btn);

        chart.create(getMeasure(this.chart2Btn, this.diff), [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        }, {
            name: ucFirst(this.chart2Btn),
            type: "number"
        }], {
            colors: [themeColors.color3],
            yAxis: [{
                "plot": {
                    "value": ucFirst(this.chart2Btn),
                    type: 'column'
                },
                "format": {"suffix": this.sensor.unit},
                title: ''
            }]
        });
    }

    updateChart3(chart) {
        let scheme = [];
        scheme.push({
            name: "Time",
            type: "date",
            format: "%Y-%m-%d"
        });
        this.measures.forEach((m) => {
            scheme.push({name: ucFirst(m), type: "number"});
        });
        chart.elem.find('.js-sensor-measure').text(this.measures.join(', '));

        chart.create(this.allData, scheme, {
            navigator: true,
            yAxis: [{
                "plot": this.measures.map((m) => ({value: ucFirst(m)})),
                "format": {"suffix": this.sensor.unit},
                title: ''
            }]
        });
    }
}