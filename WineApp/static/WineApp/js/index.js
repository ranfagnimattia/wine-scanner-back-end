class Dashboard {
    static initButtons() {
        Popper.Defaults.modifiers.computeStyle.gpuAcceleration = !(window.devicePixelRatio < 1.5 && /Win/.test(navigator.platform));

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
                console.log(month + '-' + year + ' ' + monthName);
            }
            // allDaySlot: false,
            // selectHelper: true,
            // select: function (start, end, allDay) {
            //     var title = prompt('Event Title:');
            //     if (title) {
            //         calendar.fullCalendar('renderEvent',
            //             {
            //                 title: title,
            //                 start: start,
            //                 end: end,
            //                 allDay: allDay
            //             },
            //             true // make the event "stick"
            //         );
            //     }
            //     calendar.fullCalendar('unselect');
            // }
        });
        return null;
    }

    update(data) {
        this.sensor = data.sensor;

        this.allAnomalies = data.allAnomalies;
        this.anomaliesStats = data.anomaliesStats;
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

        const anomaliesMonth = [];
        const anomaliesTot = [];
        ['minor', 'medium', 'major'].forEach((type) => {
            anomaliesMonth.push([$('.js-' + type + '-month'), this.anomaliesStats['lastMonth'][type], Animation.INT]);
            anomaliesTot.push([$('.js-' + type + '-tot'), this.anomaliesStats['tot'][type], Animation.INT]);
        });
        animation.setValues(anomaliesMonth, $('.js-anomalies-month-space'));
        animation.setValues(anomaliesTot, $('.js-anomalies-tot-space'));
    }
}