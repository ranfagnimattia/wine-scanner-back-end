function setStars(n) {
    if (n >= 0) {
        $("[id^='star-']").removeClass("checked");
    }
    if (n >= 1) {
        setTimeout(function() {
            $("#star-1").addClass("checked");
        }, 800);
    }
    if (n >= 2) {
        setTimeout(function() {
            $("#star-2").addClass("checked");
        }, 1000);
    }
    if (n >= 3) {
        setTimeout(function() {
            $("#star-3").addClass("checked");
        }, 1200);
    }
    if (n >= 4) {
        setTimeout(function() {
            $("#star-4").addClass("checked");
        }, 1400);
    }
    if (n >= 5) {
        setTimeout(function() {
            $("#star-5").addClass("checked");
        }, 1600);
    }
};

function activateSubmitButton(sel) {
    $(sel).attr('disabled', false);
    $(sel).html('Ok');
};

function deactivateSubmitButton(sel) {
    $(sel).attr('disabled', true);
    $(sel).html('<span class="loading"><i class="fa fa-spinner fa-spin mr-2"></i>Caricamento</span>');
};

function resetForecastsResults() {
    setStars(0);
    $("#forecast-results").html('');
};

function shortContent() {
    if ($(window).height() > $("body").height()) {
        $("footer").addClass("fixed-footer");
    }
    else {
        $("footer").removeClass("fixed-footer");
    }
};

function ajaxForecast(postData, limitQuality) {
    $.ajax({
        url: "ajax/getForecast",
        type: "POST",
        data: postData,
        datatype: "json",
        success: function(data) {
            resetForecastsResults();
            activateSubmitButton("#forecast-form button[type=submit]");
            if (data["err_msg"]) {
                $("#forecast-error").html('<div class="alert alert-danger" role="alert">Errore: ' + data["err_msg"] + '</div>');
            } else {
                $("#forecast-error").html('');
                floatQuality = data["quality"];
                if (limitQuality) {
                    if (floatQuality > 5) {
                        floatQuality = 5.0;
                    } 
                    else if (floatQuality < 0) {
                        floatQuality = 0;
                    }
                };
                intQuality = Math.round(floatQuality);
                setStars(intQuality);
                $("#forecast-results").html('<div>Anno: <span class="numbers">' + $("#forecastYear").val() + '</span></div><div>Qualità prevista per il Brunello di Montalcino: <span class="numbers">' + floatQuality + '</span></div>');
            };
            console.log(data);
        },
        error: function(data) {
            resetForecastsResults();
            activateSubmitButton("#forecast-form button[type=submit]");
            $("#forecast-error").html('<div class="alert alert-danger" role="alert">Errore: durante la comunicazione con il server.</div>');
        }
    });
};

$(document).ready(function() {
    
    shortContent();
    $(window).on('resize', function() {
        shortContent();
    });
    
    var navToggle = false;
    $(".navbar-toggler").on('click', function() {
        if (navToggle) {
            setTimeout(function(){
                $("nav").removeClass("navbar-light bg-white");
                navToggle = false;
            }, 310);
        } else {
            $("nav").addClass("navbar-light bg-white");
            navToggle = true;
        }
    });
    
    $('#top-btn').hide();
    $(window).scroll(function() {
        if ($(this).scrollTop() > 20) {
            $('#top-btn').fadeIn();
        } else {
            $('#top-btn').fadeOut();
        }
    });
    
    $('#top-btn').click(function() {
        $("html, body").animate({
            scrollTop: 0
        }, 500);
        return false;
    });
    
    $(".readonly").on('keydown paste', function(e){
        e.preventDefault();
    });
    
    try {
        var startDateParts = startDateString.split("/");
        var startDate = new Date(+startDateParts[2], startDateParts[1] - 1, +startDateParts[0]);

        var endDateParts = endDateString.split("/");
        var endDate = new Date(+endDateParts[2], endDateParts[1] - 1, +endDateParts[0]);
        
        var startDatepicker = $('#startDate').datepicker({
            language: 'en',
            firstDay: 1,
            dateFormat: 'dd/mm/yyyy',
            view: "years",
            autoClose: true,
            minDate: startDate,
            maxDate: endDate,
            onSelect: function(fd, d, picker) {
                if (d > startDate) {
                    var nextPicker = $('#endDate').datepicker().data('datepicker');
                    nextPicker.update({
                        minDate: d
                    })
                } 
            }
        }).data('datepicker');

        var endDatepicker = $('#endDate').datepicker({
            language: 'en',
            firstDay: 1,
            dateFormat: 'dd/mm/yyyy',
            view: "years",
            autoClose: true,
            minDate: startDate,
            maxDate: endDate,
            onSelect: function(fd, d, picker) {
                if (d < endDate) {
                    var nextPicker = $('#startDate').datepicker().data('datepicker');
                    nextPicker.update({
                        maxDate: d
                    })
                } 
            }
        }).data('datepicker');

        startDatepicker.selectDate(startDate);
        endDatepicker.selectDate(endDate);

        $('#forecastYear').datepicker({
            language: 'en',
            firstDay: 1,
            dateFormat: 'yyyy',
            view: "years",
            minView: "years",
            autoClose: true,
            minDate: startDate,
            maxDate: endDate,
            position: "top right"
        });
    } 
    catch(err) {
        console.log("No datepickers to initialize");
    };
    
});