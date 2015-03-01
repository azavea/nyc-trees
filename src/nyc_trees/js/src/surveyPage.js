"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    Handlebars = require('handlebars'),
    toastr = require('toastr'),
    mapModule = require('./map'),
    mapUtil = require('./lib/mapUtil'),
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer');

// Extends the leaflet object
require('leaflet-utfgrid');

var dom = {
        selectStartingPoint: '#select-starting-point',
        selectSide: '#select-side',

        leftButton: '#btn-left',
        leftRightButtons: '#btn-left, #btn-right',

        btnGroupNext: '#btn-group-next',
        btnNext: '#btn-next',

        pageContainer: '#pages',
        surveyPage: '#survey',
        treeFormTemplate: '#tree-form-template',
        treeFormcontainer: '#tree-form-container',
        distanceToEnd: '#distance_to_end',

        addTree: '#another-tree',
        submitSurvey: '#submit-survey'
    },

    formTemplate = Handlebars.compile($(dom.treeFormTemplate).html()),

    blockfaceId = mapUtil.getBlockfaceIdFromUrl(),
    blockfaceMap = mapModule.create({
        legend: false,
        search: false
    }),

    endPointLayers = new L.FeatureGroup(),
    defaultStyle = {
        opacity: 0.7,
        weight: 2,
        color: '#4575b4',
        clickable: true,
        radius: 25
    },
    selectStyle = {
        opacity: 0.9,
        weight: 3,
        color: '#ff0000',
        clickable: false
    },

    tileLayer = mapModule.addTileLayer(blockfaceMap),
    grid = mapModule.addGridLayer(blockfaceMap),

    selectedLayer = new SelectableBlockfaceLayer(blockfaceMap, grid, {
        onAdd: function(gridData, geom) {
            var latLngs = mapUtil.getLatLngs(geom);

            blockfaceId = gridData.id;

            selectedLayer.clearLayers();
            endPointLayers.clearLayers();

            var startCircle = L.circleMarker(latLngs[0], defaultStyle),
                endCircle = L.circleMarker(latLngs[latLngs.length - 1], defaultStyle);

            startCircle.isStart = true;
            endCircle.isStart = false;

            endPointLayers.addLayer(startCircle);
            endPointLayers.addLayer(endCircle);

            $(dom.selectSide).addClass('hidden');
            $(dom.btnGroupNext).addClass('hidden');

            mapUtil.zoomToBlockface(blockfaceMap, blockfaceId);
            return true;
        }
    }),

    isMappedFromStartOfLine = null;

blockfaceMap.addLayer(selectedLayer);
blockfaceMap.addLayer(endPointLayers);

endPointLayers.setStyle(defaultStyle);
endPointLayers.on('click', function(e) {
    endPointLayers.setStyle(defaultStyle);
    e.layer.setStyle(selectStyle);

    isMappedFromStartOfLine = e.layer.isStart;

    $(dom.selectStartingPoint).addClass('hidden');
    $(dom.leftRightButtons).removeClass('active');
    $(dom.selectSide).removeClass('hidden');
    $(dom.btnGroupNext).addClass('hidden');
});

$(dom.leftRightButtons).click(function(e) {
    $(dom.leftRightButtons).removeClass('active');
    $(this).addClass('active');
    $(dom.btnGroupNext).removeClass('hidden');
});

mapUtil.fetchBlockface(blockfaceId).done(function(blockface) {
    selectedLayer.addBlockface(blockface);
});

function showPage(selector) {
    var pages = $(dom.pageContainer).children();
    pages.addClass('hidden');
    pages.filter(selector).removeClass('hidden');
}

// There is no attribute for requiring "one or more" of a group of checkboxes to
// be selected, so we have to handle it ourselves.
$(dom.treeFormcontainer).on('change', 'input[name="problems"]', function () {
    var $form = $(this).closest('form');
    var $checkboxes = $form.find('input[name="problems"]');

    if ($checkboxes.filter(':checked').length === 0) {
        $checkboxes.prop('required', true);
    } else {
        $checkboxes.prop('required', false);
    }
});

// When "No problems" is selected, we should clear all of the other options
$(dom.treeFormcontainer).on('change', 'input[name="problems"][value="None"]', function () {
    var $form = $(this).closest('form');
    var $checkboxes = $form.find('input[name="problems"]').not(this);

    if ($(this).is(':checked')) {
        $checkboxes.prop('checked', false);
    }
});

// When other problems are checked, "No problems" should be cleared
$(dom.treeFormcontainer).on('change', 'input[name="problems"]:not([value="None"])', function () {
    var $form = $(this).closest('form');
    var $noProblems = $form.find('input[name="problems"][value="None"]');

    if ($(this).is(':checked')) {
        $noProblems.prop('checked', false);
    }
});

// When "Status" is changed, we should show/hide the appropriate sections
$(dom.treeFormcontainer).on('change', 'input[name="status"]', function () {
    var $form = $(this).closest('form');
    var $sections = $form.find('[data-status]');
    var currentStatus = $form.find('input[name="status"]:checked').val();

    $sections.addClass('hidden');
    $sections.filter('[data-status="' + currentStatus + '"]').removeClass('hidden');
});

// Helper for checking the validity of forms
function checkFormValidity($forms) {
    var valid = true;

    // Disable things we don't want to validate. Prevents the browser
    // complaining about unfocusable elements
    $forms.find('input, select, textarea')
        .not(':visible')
        .not('[data-class="fake-submit"]')
        .attr('disabled', true);

    // For each form element
    $forms.find('input, select, textarea').each(function(i, el) {
        if ($(el).is(':visible') && !el.validity.valid) {
            valid = false;

            $(el).focus();
            if (el.select) {
                el.select();
            }

            // "submit" the form.  This will trigger the builtin browser validation messages.
            // Our submit handler will prevent this from actually submitting
            $(el).closest('form').find('[data-class="fake-submit"]').click();

            return false;
        }
    });

    // Reenable things now that we're done validating
    $forms.find('input, select, textarea').attr('disabled', false);

    return valid;
}

// We need to submit the form to see the error bubbles, but we don't want to
// actually send any data.
$(dom.surveyPage).on('submit', 'form', function(e) {
    e.preventDefault();
});


$(dom.btnNext).click(function(e) {
    showPage(dom.surveyPage);
});

$(dom.addTree).click(function (){
    var $treeForms = $(dom.treeFormcontainer).find('[data-class="tree-form"]'),
        $lastTreeForm = $treeForms.last();

    if (checkFormValidity($lastTreeForm)) {
        var treeNumber = $treeForms.length + 1;

        $(dom.treeFormcontainer).append(formTemplate({tree_number: treeNumber}));
    }
});

function getTreeData(i, form) {
    var formArray = $(form).find('input,select').not(':hidden').serializeArray(),
        obj = {};

    $.each(formArray, function(i, o){
        // Diameter needs to be converted to circumference
        if ('stump_diameter' === o.name) {
            obj.circumference = obj.value * Math.PI;
        // We need to explicitly serialize "problems" as a list, and append to it
        } else if ('problems' === o.name) {
            if (! obj.problems) {
                obj.problems = [];
            }
            obj.problems.push(o.value);
        } else {
            obj[o.name] = o.value;
        }
    });

    return obj;
}

$(dom.submitSurvey).on('click', submitSurveyWithTrees);

function submitSurveyWithTrees() {
    var $forms = $(dom.surveyPage).find('form'),
        $treeForms = $forms.filter('[data-class="tree-form"]');

    if (checkFormValidity($forms)) {
        // Disable submit button to prevent double POSTs
        $(dom.submitSurvey).off('click', submitSurveyWithTrees);

        var treeData = $treeForms.map(getTreeData).get();

        // Only the last tree has "distance_to_end", so it gets special handling
        treeData[treeData.length - 1].distance_to_end = $(dom.distanceToEnd).val();

        var data = {
            survey: {
                blockface_id: blockfaceId,
                has_trees: true,
                is_mapped_in_blockface_polyline_direction: isMappedFromStartOfLine,
                is_left_side: $(dom.leftButton).is('active')
            },
            trees: treeData
        };

        // There are two views we could POST to, 'survey' and
        // 'survey_from_event', depending on how we got to this page.
        //
        // Both share the same route as the view for this page, so we should be
        // able to POST to our current URL, whatever it may be (which is the
        // $.ajax default).
        $.ajax({
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(data)
        })
        .done(function(content) {
            window.alert('Successfully saved survey');
            // TODO: Go to preview page
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            toastr.warning('Double-check your survey and try resubmitting it.', 'Something went wrong...');
        })
        .always(function() {
            // Re-enable the submit button
            $(dom.submitSurvey).on('click', submitSurveyWithTrees);
        });
    }
}
