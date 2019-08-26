/**
 * @param data.lastDayStats.maxTime
 * @param data.lastDayStats.minTime
 * @param data.trend.lastDay
 */
class Dashboard {
    static initButtons() {
        return {chart2: ['Avg', 'Diff']};
    }

    update(data) {
        this.sensor = data.sensor;
        this.mainMeasure = data.mainMeasure;

        this.allData = data.allData;
        this.last24h = data.last24h;
        this.diff = data.diff;

        this.last = data.last;
        this.lastTime = data.lastTime;
        this.lastDayStats = data.lastDayStats;
        this.trend = data.trend;

        this.lastWeekTime = data.lastWeekTime;
    }


    updateCards(animation) {
        $('.js-main-measure').text(this.mainMeasure);

        animation.setValues([
            [$('.js-last-value'), this.last],
            [$('.js-last-time'), this.lastTime, Animation.TIME],
            [$('.js-lastDay-mainMeasure'), this.lastDayStats[this.mainMeasure]]
        ], $('.js-last-space'));
        animation.setValues([
            [$('.js-lastDay-max'), this.lastDayStats.max],
            [$('.js-lastDay-maxTime'), this.lastDayStats.maxTime, Animation.TIME],
            [$('.js-lastDay-min'), this.lastDayStats.min],
            [$('.js-lastDay-minTime'), this.lastDayStats.minTime, Animation.TIME]
        ], $('.js-lastDay-space'));
        animation.setValues([
            setUpTrend($('.js-trend-previous'), this.trend.previous),
            setUpTrend($('.js-trend-lastDay'), this.trend.lastDay),
        ], $('.js-trend-space'));
    }

    /* Charts */
    updateChart1(chart) {
        chart.create(this.last24h, [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d %H:%M:%S"
        }, {
            name: 'Rilevazione',
            type: "number"
        }], {
            colors: [themeColors.color2],
            yAxis: {
                "plot": {
                    "value": 'Rilevazione',
                    connectNullData: true,
                    type: 'smooth-area',
                    style: {'area': {"fill-opacity": 0.15}}
                },
                "format": {"suffix": this.sensor.unit}
            },
            limits: this.sensor
        });
    }

    updateChart2(chart) {
        let title;
        if (this.chart2Btn === 'avg') {
            title = 'Media';
            chart.setCategory('Media ' + this.sensor.name + ' ultima settimana per fascia oraria');
        } else {
            title = 'Differenza';
            chart.setCategory(this.sensor.name + ' rispetto all\'ultima settimana per fascia oraria');
        }
        chart.setTitle(title);

        chart.create(this.diff[this.chart2Btn], [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d %H"
        }, {
            name: title,
            type: "number"
        }], {
            colors: [themeColors.color3],
            yAxis: {
                "plot": {
                    "value": title,
                    connectNullData: true,
                    type: 'column'
                },
                "format": {"suffix": this.sensor.unit}
            },
            limits: this.chart2Btn === 'avg' ? this.sensor : undefined,
            onlyHours: this.chart2Btn === 'avg'
        });
    }

    updateChart3(chart) {
        chart.create(this.allData, [{
            name: "Time",
            type: "date",
            format: "%Y-%m-%d %H:%M:%S"
        }, {
            name: 'Rilevazione',
            type: "number"
        }], {
            navigator: true,
            yAxis: {
                "plot": {
                    value: 'Rilevazione',
                    connectNullData: true
                },
                "format": {"suffix": this.sensor.unit}
            },
            initialInterval: {
                from: this.lastWeekTime
            },
            limits: this.sensor
        });
    }
}