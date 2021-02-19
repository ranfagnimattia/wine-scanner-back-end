var startTrainDate;
var endTrainDate;
var trainingResults;
var selectedComboId;

function resetTrainResults() {
    $("#model-select .list-group").html('');
    selectedComboId = null;
    trainingResults = null;
    $("#model-select").addClass('d-none');
};

$(document).ready(function() {
    
    $("#train-form").submit(function(e) {
        console.log($("#startDate").val());
        deactivateSubmitButton("#train-form button[type=submit]");
        e.preventDefault();
        $.ajax({
            url: "ajax/getBestRegressors",
            type: "POST",
            data: {
                csrfmiddlewaretoken: csfrtoken,
                startDate: $("#startDate").val(),
                endDate: $("#endDate").val()
            },
            datatype: "json",
            success: function(data) {
                activateSubmitButton("#train-form button[type=submit]");
                resetTrainResults();
                resetForecastsResults();
                if (data["err_msg"]) {
                    $("#training-error").html('<div class="alert alert-danger" role="alert">Errore: ' + data["err_msg"] + '</div>');
                } else {
                    $("#training-error").html('');
                    startTrainDate = $("#startDate").val();
                    endTrainDate = $("#endDate").val();
                    $("#model-select").removeClass('d-none');
                    trainingResults = data;
                    trainingResults["results"].forEach(function(value, index) {
                        $("#model-select .list-group").append('<button type="button" id="combo-' + index + '" class="list-group-item list-group-item-blue list-group-item-action text-justify d-flex flex-nowrap"><div><span class="badge badge-custom badge-pill mr-3">' + (index + 1) + '</span></div><div class="flex-grow-1"></div></button>');
                        for (i=0; i < value["regr_list"].length; i++) {
                            $("#combo-" + index + " > div.flex-grow-1").append('<div class="d-flex justify-content-between align-items-center"><span class="regr-name">' + value["regr_list"][i] + '</span><span class="badge badge-custom badge-pill mx-2 d-none d-sm-block"><i class="' + value["icons"][i] + '"></i></span></div>');
                            if (value["regr_list"][i] == "Indice di Winkler") {
                                $("#combo-" + index + " > div.flex-grow-1 > div.d-flex:last-child > .regr-name").append('<button type="button" class="btn btn-help ml-3" data-toggle="modal" data-target="#winkler-modal">?</button>');
                            } 
                            else if (value["regr_list"][i] == "Indice di Huglin") {
                                $("#combo-" + index + " > div.flex-grow-1 > div.d-flex:last-child > .regr-name").append('<button type="button" class="btn btn-help ml-3" data-toggle="modal" data-target="#huglin-modal">?</button>');
                            } 
                            else if (value["regr_list"][i] == "GST") {
                                $("#combo-" + index + " > div.flex-grow-1 > div.d-flex:last-child > .regr-name").append('<button type="button" class="btn btn-help ml-3" data-toggle="modal" data-target="#gst-modal">?</button>');
                            }
                        };
                    });
                    shortContent();
                };
                console.log(data);
            },
            error: function(data) {
                activateSubmitButton("#train-form button[type=submit]");
                resetTrainResults();
                resetForecastsResults();
                $("#training-error").html('<div class="alert alert-danger" role="alert">Errore: durante la comunicazione con il server.</div>');
                shortContent();
            }
        });
    });
    
    $("#model-select").on('click', "button[id^='combo-']", function() {
        selectedComboId = $(this).attr('id').slice(-1);
        $("[id^=combo-]").removeClass("active");
        $(this).addClass("active");
    });
    
    $("#forecast-form").submit(function(e) {
        deactivateSubmitButton("#forecast-form button[type=submit]");
        e.preventDefault();
        if (selectedComboId == null) {
            $("#forecast-error").html('<div class="alert alert-danger" role="alert">Errore: nessun modello selezionato.</div>');
            activateSubmitButton("#forecast-form button[type=submit]")
        } else {
            $("#forecast-error").html('');
            postData = {
                csrfmiddlewaretoken: csfrtoken,
                startTrainDate: startTrainDate,
                endTrainDate: endTrainDate,
                forecastYear: $("#forecastYear").val(),
                regrCombo: trainingResults["results"][selectedComboId]['regr_combo']
            };
            ajaxForecast(postData, limitQuality=true);
        }
    });
});