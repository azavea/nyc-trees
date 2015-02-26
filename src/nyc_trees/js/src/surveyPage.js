"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    Handlebars = require('handlebars'),
    mapModule = require('./map'),
    mapUtil = require('./lib/mapUtil'),
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer');

// Extends the leaflet object
require('leaflet-utfgrid');

var dom = {
    selectStartingPoint: '#select-starting-point',
    selectSide: '#select-side',
    leftRightButtons: '#btn-left, #btn-right',
    btnGroupNext: '#btn-group-next',
    btnNext: '#btn-next',

    pageContainer: '#pages',
    surveyPage: '#survey',
    treeFormTemplate: '#tree-form-template',
    treeFormcontainer: '#tree-form-container',

    addTree: '#another-tree',
    submitSurvey: '#submit-survey'
};

var formTemplate = Handlebars.compile($(dom.treeFormTemplate).html());

var blockfaceId = mapUtil.getBlockfaceIdFromUrl(),
    blockfaceMap = mapModule.create({
        legend: true,
        search: true
    });

var endPointLayers = new L.FeatureGroup(),
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
    };

var tileLayer = mapModule.addTileLayer(blockfaceMap),
    grid = mapModule.addGridLayer(blockfaceMap),

    selectedLayer = new SelectableBlockfaceLayer(blockfaceMap, grid, {
        onAdd: function(gridData, geom) {
            var latLngs = mapUtil.getLatLngs(geom);

            blockfaceId = gridData.id;

            selectedLayer.clearLayers();
            endPointLayers.clearLayers();

            endPointLayers.addLayer(
                L.circleMarker(latLngs[0], defaultStyle)
            );
            endPointLayers.addLayer(
                L.circleMarker(latLngs[latLngs.length - 1], defaultStyle)
            );

            $(dom.selectSide).addClass('hidden');
            $(dom.btnGroupNext).addClass('hidden');

            mapUtil.zoomToBlockface(blockfaceMap, blockfaceId);
            return true;
        }
    });

blockfaceMap.addLayer(selectedLayer);
blockfaceMap.addLayer(endPointLayers);

endPointLayers.setStyle(defaultStyle);
endPointLayers.on('click', function(e) {
    endPointLayers.setStyle(defaultStyle);
    e.layer.setStyle(selectStyle);

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

// There is attribute for requiring "one or more" of a group of checkboxes to
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

// Helper for checking the validity of a form
function checkFormValidity() {
    var $forms = $(dom.treeFormcontainer).find('form');
    var valid = true;

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

    return valid;
}

// We need to submit the form to see the error bubbles, but we don't want to
// actually send any data.
$(dom.treeFormcontainer).on('submit', 'form', function(e) {
    e.preventDefault();
});


$(dom.btnNext).click(function(e) {
    showPage(dom.surveyPage);
});

$(dom.addTree).click(function (){
    if (checkFormValidity()) {
        var treeNumber = $(dom.treeFormcontainer).find('[data-class="tree-form"]').length + 1;

        $(dom.treeFormcontainer).append(formTemplate({tree_number: treeNumber}));
    }
});

$(dom.submitSurvey).on('click', function() {
    // TODO: replace this with data from the form(s)
    var data = {
        survey: {
            blockface_id: blockfaceId,
            is_flagged: false,
            has_trees: true,
            is_mapped_in_blockface_polyline_direction: true,
            is_left_side: true
        },
        trees: [
            {
                circumference: 10,
                distance_to_tree: 100,
                curb_location: 'OnCurb',
                status: 'Alive',
                species_certainty: 'Yes',
                health: 'Good',
                stewardship: 'None',
                guards: 'None',
                sidewalk_damage: 'NoDamage',
                problems: ['Stones', 'Sneakers']
            }
        ]
    };
    $.ajax('/survey/', {
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(data)
        })
        .done(function(content) {
            window.alert('Successfully saved a test survey');
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            window.alert(errorThrown);
        });
});
