function vintageCountFromStrings(start, end, id) {
    start_int = parseInt(start.slice(-4));
    end_int = parseInt(end.slice(-4));
    vintages = end_int - start_int + 1;
    $(id).html(vintages);
};

$(document).ready(function() {

    $("#training-form").submit(function() {
        deactivateSubmitButton("#training-form button[type=submit]");
    });
    
    $(window).on('unload', function() {
        activateSubmitButton("#training-form button[type=submit]");
    });
    
    $("#forecast-form").submit(function(e) {
        deactivateSubmitButton("#forecast-form button[type=submit]");
        e.preventDefault();
        postData["forecastYear"] = $("#forecastYear").val();
        ajaxForecast(postData, limitQuality=false);
    });
    
});