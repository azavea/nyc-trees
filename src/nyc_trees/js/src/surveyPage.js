"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    Handlebars = require('handlebars'),
    toastr = require('toastr'),
    mapModule = require('./map'),
    mapUtil = require('./lib/mapUtil'),
    BlockfaceLayer = require('./lib/BlockfaceLayer'),
    valIsEmpty = require('./lib/valIsEmpty'),
    mapAnotherPopup = require('./mapAnotherPopup'),
    stickyTitlesModule = require('./lib/stickyTitles'),

    statePrompter = require('./lib/statePrompter').init({
        warning: 'You have begun mapping this block edge but have not saved your work.',
        question: ''
    });

// Extends the leaflet object
require('leaflet-utfgrid');

// Extends jQuery
require('select2');

var makeMutexShow = (function() {
    /*
     Build function that will show a set of elements and hide
     any other elements that has been passed to makeMutexShow

     Example:

     var showGroupOne = makeMutexShow(['a', 'b']);
     var showGroupTwo = makeMutexShow(['a', 'c']);
     var showGroupThree = makeMutexShow(['d']);

     showGroupOne();   // a and b are shown, c and d are hidden
     showGroupTwo();   // a and c are shown, b and d are hidden
     showGroupThree(); // d is shown, a, b, and c are hidden

     */
    var allSelectors = [];
    return function(selectorsInThisGroup){
        allSelectors = allSelectors.concat(selectorsInThisGroup);
        return function() {
            $.each(allSelectors, function(i, selector){
                if ($.inArray(selector, selectorsInThisGroup) >= 0) {
                    $(selector).removeClass('hidden');
                } else {
                    $(selector).addClass('hidden');
                }
            });
        };
    };
}());

var dom = {
        geolocateButton: '.geolocate-button',

        selectStartingPoint: '#select-starting-point',
        selectSide: '#select-side',

        leftButton: '#btn-left',
        leftRightButtons: '#btn-left, #btn-right',

        btnGroupNext: '#btn-group-next',
        btnNext: '#btn-next',

        mainHeader: '.main-header',
        mapSidebar: '.map-sidebar',
        actionBar: '.action-bar-survey',
        surveyPage: '#survey',
        treeFormTemplate: '#tree-form-template',
        treeFormcontainer: '#tree-form-container',
        distanceToEnd: '#distance_to_end',
        treeForms: '[data-class="tree-form"]',
        collapseButton: '[data-toggle="collapse"]',
        fieldset: 'fieldset',

        addTree: '#another-tree',
        noFurtherTrees: '#no-further-trees',
        submitSurvey: '#submit-survey',

        noFurtherTreesGroup: '#no-further-trees-group',

        deleteTree: '[data-action="delete"]',
        deleteTreePopup: '#delete-tree-popup',
        deleteTreeConfirm: '#delete-tree-confirm',

        quitPopup: '#quit-popup',
        quitShowPopup: '#cant-map',
        quitReason: '#quit-reason',
        quit: '#quit',

        previewHelpPopup: '#preview-button-help',

        btnGroupToTeammate: '#btn-group-to-teammate',
        btnToTeammate: '#btn-to-teammate',
        selectTeammate: '#select-teammate',
        teammateSelectElement: '#teammate-select',

        btnNoTrees: '#no-trees',
        noTreesPopup: '#no-trees-popup',
        noTreesConfirm: '#no-trees-confirm',

        treeHeading: '.sticky-title',
        blockId: '[data-block-id]',

        previewButton: '#preview-survey',
        closePreviewSection: '#close-preview-section',
        closePreview: '#close-preview',
        restartSurvey: '#restart-survey',

        blockfaceMapId: 'map',
        previewMapId: 'preview-map'
    },

    showSelectStart = makeMutexShow([
        dom.selectStartingPoint
    ]),

    showSelectSide = makeMutexShow([
        dom.selectSide,
        dom.leftRightButtons
    ]),

    showSelectSideNext = makeMutexShow([
        dom.selectSide,
        dom.leftRightButtons,
        dom.btnGroupToTeammate
    ]),

    showSelectTeammate = makeMutexShow([
        dom.selectTeammate,
        dom.btnGroupNext
    ]),

    formTemplate = Handlebars.compile($(dom.treeFormTemplate).html()),

    blockfaceId = mapUtil.getBlockfaceIdFromUrl(),
    mapObjects = mapModule.createAndGetControls({
        domId: dom.blockfaceMapId,
        legend: false,
        search: true,
        geolocation: true,
        crosshairs: true
    }),
    blockfaceMap = mapObjects.map,
    multiControl = mapObjects.multiControl,

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
    grid = mapModule.addGridLayer(blockfaceMap, { crosshairs: true }),

    selectedLayer = new BlockfaceLayer(blockfaceMap, { color: '#FFEB3B' }),

    isMappedFromStartOfLine = null,

    mapInteractionEnabled = true,

    stickyTitles = stickyTitlesModule(
        $(window), dom.treeHeading, $(dom.actionBar)),

    previewMap = null,
    previewLayer = null,
    savedScrollPosition = 0;

statePrompter.lock();

selectedLayer.clicksEnabled = false;
blockfaceMap.addLayer(selectedLayer);
blockfaceMap.addLayer(endPointLayers);
mapModule.startTrackingUserPosition(blockfaceMap);

grid.on('mapMove', function(e) {
    var data = e.data;
    if (data && data.survey_type === 'available' && data.id !== blockfaceId) {
        selectBlockface(data);
    }
});

function selectBlockface(data) {
    blockfaceId = data.id;

    var geom = mapUtil.parseGeoJSON(data.geojson),
        latLngs = mapUtil.getLatLngs(geom),
        startCircle = L.circleMarker(latLngs[0], defaultStyle),
        endCircle = L.circleMarker(latLngs[latLngs.length - 1], defaultStyle);

    startCircle.isStart = true;
    endCircle.isStart = false;

    selectedLayer.clearLayers();
    endPointLayers.clearLayers();

    selectedLayer.addData({
        "type": "Feature",
        "geometry": geom
    });
    endPointLayers.addLayer(startCircle);
    endPointLayers.addLayer(endCircle);

    showSelectStart();

    $(dom.blockId).html(Number(blockfaceId).toLocaleString());
}

endPointLayers.setStyle(defaultStyle);
endPointLayers.on('click', function(e) {
    if (!mapInteractionEnabled) {
        return;
    }
    endPointLayers.setStyle(defaultStyle);
    e.layer.setStyle(selectStyle);

    isMappedFromStartOfLine = e.layer.isStart;

    $(dom.leftRightButtons).removeClass('active');
    showSelectSide();
});

$(dom.leftRightButtons).click(function(e) {
    $(dom.leftRightButtons).removeClass('active');
    $(this).addClass('active');
    showSelectSideNext();
});

$(dom.btnToTeammate).click(function(e) {
    showSelectTeammate();
});

mapUtil.fetchBlockface(blockfaceId).done(selectBlockface);

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

function getSectionToggleHandler(fieldName) {
    return function () {
        var $form = $(this).closest('form');
        var $sections = $form.find('[data-' + fieldName + ']');
        var currentStatus = $form.find('input[name="' + fieldName + '"]:checked').val() || "";

        if (currentStatus) {
            $sections.addClass('hidden');
            // Note that we use '~=` which selects from a whitespace deliminated list
            $sections.filter('[data-' + fieldName + '~="' + currentStatus + '"]').removeClass('hidden');
        } else {
            $sections.removeClass('hidden');
        }
    };
}

// When "Status" is changed, we should show/hide the appropriate sections
$(dom.treeFormcontainer).on('change', 'input[name="status"]', getSectionToggleHandler('status'));

// When "Tree Guard" is changed, we should show/hide the appropriate sections
$(dom.treeFormcontainer).on('change', 'input[name="guard_installation"]', getSectionToggleHandler('guard_installation'));

// When "No Problems" is changed, we should show/hide the appropriate sections
$(dom.treeFormcontainer).on('change', 'input[name="problems"][value="None"]', getSectionToggleHandler('problems'));

// Helper for checking the validity of forms
function checkFormValidity($forms) {
    var valid = true;

    // If any forms are collapsed, show them temporarily
    $forms.removeClass('collapse');

    // Disable things we don't want to validate. Prevents the browser
    // complaining about unfocusable elements
    var $disabledElems = $forms.find('input, select, textarea')
        .not(':visible')
        .not('[data-class="fake-submit"]');

    $disabledElems.attr('disabled', true);

    var $elemToFocus = null;

    // For each form element
    $forms.find('input, select, textarea').each(function(i, el) {
        var $el = $(el),
            $error = getErrorlistForElement($el);

        $error.hide();
        if ($el.is(':visible') && !el.validity.valid) {
            $error.show();

            // We keep a handle to the first invalid element so we can scroll to it.
            if (valid) {
                valid = false;
                $elemToFocus = $el;
            }
        }
    });

    // If there is more than one form, re-collapse them now that we're done validating
    if ($(dom.treeFormcontainer).find(dom.treeForms).length > 1) {
        $forms.filter(dom.treeForms).addClass('collapse');
    }

    if ($elemToFocus !== null) {
        var $form = $elemToFocus.closest('form');

        if ($form.hasClass('collapse') && $form.is(':hidden')) {
            // Make sure the form with the errors on it is not collapsed
            $elemToFocus.closest(dom.treeForms).collapse('show');

            $forms.one('shown.bs.collapse', function() {
                scrollToInvalidElement($elemToFocus, $forms, $disabledElems);
            });
        } else {
            scrollToInvalidElement($elemToFocus, $forms, $disabledElems);
        }
    } else {
        $disabledElems.attr('disabled', false);
    }

    return valid;
}

function getErrorlistForElement($el) {
    return $el.closest('form').find('.errorlist[data-name="' + $el[0].name + '"]');
}

function scrollToInvalidElement($elemToFocus, $forms, $disabledElems) {
    // Scroll so element and its label are visible
    var $fieldset = $elemToFocus.closest(dom.fieldset);
    // If we couldn't find a fieldset (likely distance to end), just scroll to the element
    var scrollPos = getScrollToTopPosition($fieldset.length > 0 ? $fieldset : $elemToFocus);
    if (isMobile()) {
        $('html,body').scrollTop(scrollPos);
    } else {
        $(dom.mapSidebar).scrollTop(scrollPos);
    }

    // Reenable things now that we're done validating
    $disabledElems.attr('disabled', false);
}

// Clear error bubbles when values change
$(dom.surveyPage).on('blur change keyup paste', function(e) {
    var $error = getErrorlistForElement($(e.target)),
        currentScroll, $scrollableElem;

    // We carefully scroll the page up with the same animation time as the
    // $error.slideDown(), so that the actual input element remains in the same
    // place on the page
    if ($error.is(':visible') && e.target.validity.valid) {
        $error.slideUp(300);

        if (isMobile()) {
            $scrollableElem = $('html,body');
            currentScroll = $(document).scrollTop();
        } else {
            $scrollableElem = $(dom.mapSidebar);
            currentScroll = $scrollableElem.scrollTop();
        }
        var newScrollPos = currentScroll - $error.outerHeight(true);
        $scrollableElem.animate({ scrollTop: newScrollPos }, 300);
    }
});

function isMobile() {
    return $(window).width() < 768;  // Bootstrap $screen-sm
}

$(dom.btnNext).click(function(e) {
    $(dom.selectSide).addClass('hidden');
    $(dom.selectTeammate).addClass('hidden');
    $(dom.surveyPage).toggleClass('hidden');
    $(dom.actionBar).addClass('expanded');
    mapInteractionEnabled = false;
    multiControl.removeFrom(blockfaceMap);
    blockfaceMap.dragging.disable();
    blockfaceMap.touchZoom.disable();
    blockfaceMap.doubleClickZoom.disable();
    blockfaceMap.scrollWheelZoom.disable();
    blockfaceMap.boxZoom.disable();
    blockfaceMap.keyboard.disable();
    blockfaceMap.removeLayer(grid);
    mapModule.hideCrosshairs();
    mapModule.stopTrackingUserPosition(blockfaceMap);

    if ($(dom.previewHelpPopup).length > 0) {
        $(dom.previewHelpPopup).modal('show');
    }
});

$(dom.addTree).click(function (){
    var $treeForms = $(dom.treeFormcontainer).find(dom.treeForms),
        $lastTreeForm = $treeForms.last();

    if (checkFormValidity($lastTreeForm)) {
        var treeNumber = $treeForms.length + 1;

        // Scroll to the first field for easier data entry
        var $lastHeader = $("#tree-header-" + (treeNumber - 1)),
            $scrollContainer = isMobile() ? $('html,body') : $(dom.mapSidebar);
        $scrollContainer.stop().animate({
            scrollTop: getScrollToTopPosition($lastHeader)
        }, 400).promise().done(function() {
            $treeForms.collapse('hide');
            $(dom.treeFormcontainer).append(formTemplate({tree_number: treeNumber}));
            var $newForm = $(dom.treeFormcontainer).find(dom.treeForms).last();
            setupSpeciesAutocomplete($newForm);

            setTimeout(function() {
                $newForm.collapse('show');
                $(dom.collapseButton).removeClass('hidden');

                // Hide delete tree button on all but last form
                var $deleteButtons = $(dom.treeFormcontainer).find(dom.deleteTree);
                $deleteButtons.addClass('hidden');
                $deleteButtons.last().removeClass('hidden');

                stickyTitles.update();
            }, 100);
        });
    }
});

$(dom.previewButton).on('click', previewSurvey);

function previewSurvey(e) {
    var $forms = $(dom.surveyPage).find('form'),
        $treeForms = $forms.filter(dom.treeForms);

    if (checkFormValidity($forms)) {
        // Disable preview button to prevent double POSTs
        $(dom.previewButton).off('click', previewSurvey);

        var data = createSurveyDataWithTrees($treeForms);

        // Keep this URL in sync with src/nyc_trees/apps/survey/urls/survey.py
        $.ajax({
            url: '/survey/preview/',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(data)
        })
        .done(showPreview)
        .fail(function(jqXHR, textStatus, errorThrown) {
            toastr.warning('Double-check your survey and try previewing it again.', 'Something went wrong...');
        })
        .always(function() {
            // Re-enable the preview button
            $(dom.previewButton).on('click', previewSurvey);
        });
    }
}

function showPreview(trees) {
    if (isMobile()) {
        // Some browsers scroll <html>, some scroll <body>, have to query both
        savedScrollPosition = $('html').scrollTop() || $('body').scrollTop();
    } else {
        savedScrollPosition = $(dom.mapSidebar).scrollTop();
    }

    $(dom.surveyPage).addClass('hidden');
    $(dom.actionBar).removeClass('expanded').addClass('skinny');
    $(dom.closePreviewSection).removeClass('hidden');
    $('#' + dom.blockfaceMapId).addClass('hidden');
    $('#' + dom.previewMapId).removeClass('hidden');

    var bounds = selectedLayer.getBounds();
    if (previewMap === null) {
        previewMap = mapModule.create({
            domId: dom.previewMapId,
            legend: false,
            search: false,
            baseMap: mapModule.SATELLITE,
            minZoom: blockfaceMap.getBoundsZoom(bounds) - 1,
        });
        previewLayer = new L.geoJson(null, {
            pointToLayer: function(feature, latLng) {
                return mapUtil.styledCircleMarker(latLng);
            }
        });
        previewLayer.addTo(previewMap);
    }
    // If the browser window is resized when the preview map is hidden
    // (from the phone switching orientation for example), the map won't display properly
    // Calling .invalidateSize() should fix that
    previewMap.invalidateSize();
    previewMap.fitBounds(bounds);
    previewMap.setMaxBounds(bounds);

    previewLayer.clearLayers();
    previewLayer.addData(selectedLayer.toGeoJSON());
    previewLayer.setStyle(mapUtil.styledStreetConfirmation);

    $.each(trees, function (__, tree) {
        previewLayer.addData({ 'type': 'Feature', 'geometry': tree });
    });
}

$(dom.closePreview).click(function () {
    $(dom.surveyPage).removeClass('hidden');
    $(dom.actionBar).addClass('expanded').removeClass('skinny');
    $(dom.closePreviewSection).addClass('hidden');
    $('#' + dom.blockfaceMapId).removeClass('hidden');
    $('#' + dom.previewMapId).addClass('hidden');

    if (isMobile()) {
        $('html,body').scrollTop(savedScrollPosition);
    } else {
        $(dom.mapSidebar).scrollTop(savedScrollPosition);
    }
    //
    // If the browser window is resized when the blockface map is hidden
    // (from the phone switching orientation for example), the map won't display properly
    // Calling .invalidateSize() should fix that
    blockfaceMap.invalidateSize();
});

function getScrollToTopPosition($el) {
    if (isMobile()) {
        return $el.offset().top - $(dom.mainHeader).height();
    } else {
        return $el.offset().top - $(dom.surveyPage).offset().top;
    }
}

$(dom.noFurtherTrees).on('click', function(e) {
    // Adding active class will reveal submit button,
    // and distance to end field
    $(dom.noFurtherTreesGroup).addClass('active');
});

// When tree forms are opened/closed we need to change the icon class of the toggle
$(dom.treeFormcontainer).on('show.bs.collapse', function(e) {
    var formId = $(e.target).attr('id'),
        $toggle = $(dom.collapseButton).filter('[data-target="#' + formId + '"]').children('i');

    $toggle.removeClass('icon-right-open-big').addClass('icon-down-open-big');
});
$(dom.treeFormcontainer).on('hide.bs.collapse', function(e) {
    var formId = $(e.target).attr('id'),
        $toggle = $(dom.collapseButton).filter('[data-target="#' + formId + '"]').children('i');

    $toggle.removeClass('icon-down-open-big').addClass('icon-right-open-big');
});
$(dom.treeFormcontainer).on('shown.bs.collapse, hidden.bs.collapse', function() {
    stickyTitles.update();
});

$(dom.treeFormcontainer).on('click', dom.deleteTree, function(e) {
    // We assume that we are dealing with the last tree form, since we only
    // show the delete button for the last tree
    var $lastTreeForm = $(dom.treeFormcontainer).find(dom.treeForms).last(),
        treeData = getTreeData($lastTreeForm),

        showWarning = false;

    for (var key in treeData) {
        if (treeData[key]) {
            showWarning = true;
        }
    }

    if (showWarning) {
        $(dom.deleteTreePopup).modal('show');
    } else {
        deleteLastTree();
    }
});

$(dom.deleteTreeConfirm).on('click', deleteLastTree);

function deleteLastTree() {
    var $lastTreeForm = $(dom.treeForms).last(),
        $lastTreeHeader = $lastTreeForm.prev();

    $lastTreeForm.remove();
    $lastTreeHeader.remove();

    // A little bit of housekeeping - we need to undo the effects of adding
    // a new tree form, with some special cases if there is only one tree left
    var $deleteButtons = $(dom.deleteTree);
    $deleteButtons.addClass('hidden');

    if ($deleteButtons.length > 1) {
        $deleteButtons.last().removeClass('hidden');
    }

    var $collapseButtons = $(dom.collapseButton);
    if ($collapseButtons.length == 1) {
        $collapseButtons.addClass('hidden');
    }

    var $newLastForm = $(dom.treeForms).last();
    $newLastForm.collapse('show');
}

function getTreeData(form) {
    var obj = {},
        $form = $(form),
        wasCollapsed = $form.hasClass('collapse');

    // Temporarily show form before serializing form fields, otherwise all
    // fields will appear to be hidden.
    $form.removeClass('collapse');

    var formArray = $form
            .find('input:not([type="submit"]),select')
            .not(':hidden')
            .serializeArray();

    $.each(formArray, function(i, o){
        // We need to explicitly serialize "problems" as a list, and append to it
        if ('problems' === o.name) {
            if (! obj.problems) {
                obj.problems = [];
            }
            obj.problems.push(o.value);
        // 'guard_installation' is not a real field, but it is secretly 'guards' for one of it's options
        } else if ('guard_installation' === o.name) {
            if (o.value === 'No') {
                obj.guards = 'None';
            }
        } else {
            obj[o.name] = o.value;
        }
    });

    if (wasCollapsed) {
        $form.addClass('collapse');
    }

    return obj;
}

$(dom.submitSurvey).on('click', submitSurveyWithTrees);

function createSurveyData() {
    return {
        survey: {
            blockface_id: blockfaceId,
            is_left_side: $(dom.leftButton).is('.active'),
            is_mapped_in_blockface_polyline_direction: isMappedFromStartOfLine,
            teammate_id: $(dom.teammateSelectElement).select2("val"),
            has_trees: undefined,
            quit_reason: undefined
        },
        trees: undefined
    };
}

function createSurveyDataWithTrees($treeForms) {
    var treeData = $treeForms.map(function(i, form) {
        return getTreeData(form);
    }).get();

    // Only the last tree has "distance_to_end", so it gets special handling
    treeData[treeData.length - 1].distance_to_end = $(dom.distanceToEnd).val();

    var data = createSurveyData();
    data.survey.has_trees = true;
    data.trees = treeData;

    return data;
}

function submitSurveyWithTrees() {
    var $forms = $(dom.surveyPage).find('form'),
        $treeForms = $forms.filter(dom.treeForms);

    if (checkFormValidity($forms)) {
        // Disable submit button to prevent double POSTs
        $(dom.submitSurvey).off('click', submitSurveyWithTrees);

        var data = createSurveyDataWithTrees($treeForms);

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
            // make sure not to take the hashstring along for the ride
            // Note: this URL needs to be kept in sync with
            // src/nyc_trees/apps/survey/urls/survey.py
            var href = window.location.origin +
                    window.location.pathname +
                    'confirm/' + content.survey_id + '/';
            statePrompter.unlock();
            window.location.href = href;
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            toastr.warning('Double-check your survey and try resubmitting it.', 'Something went wrong...');
            // Re-enable the submit button
            $(dom.submitSurvey).on('click', submitSurveyWithTrees);
        });
    }
}

$(dom.quit).on('click', quitSurvey);

function dismissAndPrompt(modalId) {
    return function(content) {
        $(modalId).modal('hide');
        statePrompter.unlock();
        mapAnotherPopup.show();
    };
}

function quitSurvey() {
    // Disable submit button to prevent double POSTs
    $(dom.quit).off('click', quitSurvey);

    var data = createSurveyData();
    data.survey.has_trees = false;
    data.survey.quit_reason = $(dom.quitReason).val();

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
    .done(dismissAndPrompt(dom.quitPopup))
    .fail(function(jqXHR, textStatus, errorThrown) {
        toastr.warning('Sorry, there was a problem stopping the survey. Please try again.', 'Something went wrong...');
    })
    .always(function() {
        // Re-enable the submit button
        $(dom.quit).on('click', quitSurvey);
    });
}

$(dom.quitShowPopup).on('click', function(e) {
    // Bootstrap will handle showing the modal, but the
    // hidden class, applied by other code, needs to be
    // removed.
    $(dom.quitPopup).removeClass('hidden');
});

// The quit button is not enabled until a quit reason is entered
$(dom.quit).prop('disabled', true);

$(dom.quitReason).on('change keyup paste', function() {
    $(dom.quit).prop('disabled', valIsEmpty(dom.quitReason));
});

$(dom.quitPopup).on('shown.bs.modal', function () {
    $(dom.quitReason).focus();
});

$(dom.teammateSelectElement).select2({
    placeholder: "Username",
    allowClear: true,
    minimumInputLength: 1,
    ajax: {
        // Note: changes here must be kept in sync with
        // src/nyc_trees/survey/urls/survey.py
        url: "/survey/teammates/",
        dataType: 'json',
        quietMillis: 100,
        data: function (term) {
            return {q: term};
        },
        results: function(data) {
            return {results: data};
        }
    }
});

$(dom.btnNoTrees).on('click', function(e) {
    // Bootstrap will handle showing the modal, but the
    // hidden class, applied by other code, needs to be
    // removed.
    $(dom.noTreesPopup).removeClass('hidden');
});

$(dom.noTreesConfirm).on('click', saveWithoutTrees);

function saveWithoutTrees() {
    // Disable submit button to prevent double POSTs
    $(dom.noTreesConfirm).off('click', saveWithoutTrees);

    var data = createSurveyData();
    data.survey.has_trees = false;

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
    .done(dismissAndPrompt(dom.noTreesPopup))
    .fail(function(jqXHR, textStatus, errorThrown) {
        toastr.warning('Sorry, there was a problem saving the survey. Please try again.', 'Something went wrong...');
    })
    .always(function() {
        // Re-enable the submit button
        $(dom.noTreesConfirm).on('click', saveWithoutTrees);
    });
}

function setupSpeciesAutocomplete($form) {
    var getFormattedData = function(state) {
        var $option = $(state.element),
            scientificName = $option.data('scientific-name').trim(),
            cultivar = $option.data('cultivar').trim(),
            commonName = state.text.trim();

        if (cultivar) {
            return {
                essentialName: "<i>" + scientificName + "</i> (" + cultivar + ")",
                commonName: commonName
            };
        } else {
            return {
                essentialName: "<i>" + scientificName + "</i>",
                commonName: commonName
            };
        }
    };

    $form.find('select[name="species_id"]').select2({
        allowClear: false,
        minimumInputLength: 3,
        placeholder: "Select and type species name",
        matcher: function(term, commonName, $option) {
            var scientificName = $option.data('scientific-name'),
                cultivar = $option.data('cultivar'),

                matches = function(content) {
                    if ($.type(content) === "string") {
                        return content.toUpperCase().indexOf(term.toUpperCase()) >= 0;
                    }
                    return false;
                };

            return matches(commonName) || matches(scientificName) || matches(cultivar);
        },

        // For the formatted selection, we need to do our best to get it on one
        // line.  It will get cut off with ellipsis if it's too long
        formatSelection: function(state) {
            var data = getFormattedData(state);

            return data.commonName + ' &mdash; ' + data.essentialName;
        },

        // For the formatted result row, it's ok to be on multiple rows
        formatResult: function(state, container, query) {
            var data = getFormattedData(state),
                html = '<p>' + data.commonName + '</p><p>' + data.essentialName + '</p>',
                index = html.toUpperCase().indexOf(query.term.toUpperCase()),
                end = Math.max(0, index) + query.term.length;

            // We add a class of 'select2-match' around the first piece of text
            // matching our query, to indicate what part matched
            if (index >= 0 && end > index) {
                return html.slice(0, index) + '<span class="select2-match">' + html.slice(index, end) + '</span>' + html.slice(end);
            } else {
                return html;
            }
        },

        escapeMarkup: function(m) { return m; }
    });
}

setupSpeciesAutocomplete($(dom.treeFormcontainer).find(dom.treeForms));

// Need to blur the Select2 element when it is closed to make sure any soft
// keyboards also are closed
$('body').on('select2-close', 'select', function() {
    setTimeout(function() {
        $('.select2-container-active').removeClass('select2-container-active');
        $('.select2-focusser:focus').blur();
    }, 1);
});

// Display help popup for geolocation button.
var helpShown = mapModule.getDomMapAttribute('geolocate-help-shown').toLowerCase() == 'true';
if (!helpShown) {
    $(dom.geolocateButton).append(
        '<div class="geolocate-help">Move the map to your location</div>'
    );
    $(document).one('click', function () {
        $('.geolocate-help').hide();
    });
}

$(dom.restartSurvey).on('click', function() {
    window.location.hash = blockfaceId;
    window.location.reload();
});
