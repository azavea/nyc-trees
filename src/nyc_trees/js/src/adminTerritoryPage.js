"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    toastr = require('toastr'),
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer');

// Extends the leaflet object
require('leaflet-utfgrid');
require('leaflet-draw');

var dom = {
        groupChooser: '#select-group',
        selectedGroupOption: '#select-group option:selected',
        areaControls: '.js-area',
        addAreaButton: '.js-area-add',
        removeAreaButton: '.js-area-remove',
        cancelAreaButton: '.js-area-cancel',
        revertButton: '.js-revert',
        saveButton: '.js-save'
    },

    territoryMap = mapModule.create({
        legend: true,
        search: true
    }),
    tileLayer = null,
    grid = null,
    selectionLayer = null,

    blockDataListForRevert = null,
    selectedBlockfaces = {},
    hasUnsavedChanges = false,
    $currentGroupOption = null;


$(document).ready(onGroupChanged);
$(dom.groupChooser).on('change', onGroupChanged);

$(dom.addAreaButton).click(drawAreaToAdd);
$(dom.removeAreaButton).click(drawAreaToRemove);
$(dom.cancelAreaButton).click(stopDrawing);

territoryMap.on('draw:created', onAreaComplete);

$(dom.revertButton).click(revertTerritory);
$(dom.saveButton).click(saveTerritory);

$(window).on('beforeunload', function(e) {
    if (hasUnsavedChanges) {
        return 'You have unsaved changes. Continue anyway?';
    } else {
        return undefined;
    }
});

function okToProceed() {
    if (hasUnsavedChanges) {
        return window.confirm('You have unsaved changes. Continue anyway?');
    } else {
        return true;
    }
}

function onGroupChanged() {
    if (okToProceed()) {
        getGroupUnmappedTerritory(initAllLayers);
        $currentGroupOption = $(dom.selectedGroupOption);
    } else {
        // Don't change group after all.
        // Dropdown has already changed, so change it back.
        $currentGroupOption.attr('selected', true);
    }
}

function getGroupUnmappedTerritory(onSuccess, polygon) {
    disableUserActions();
    $.ajax({
        // Keep this URL in sync with "group_unmapped_territory_geojson"
        // in src/nyc_trees/apps/users/urls/group.py
        url: '/group/' + currentGroupId() + '/territory.json/',
        type: 'POST',
        dataType: 'json',
        data: polygon
    })
        .done(onSuccess)
        .fail(function () {
            toastr.error("Failed to retrieve block edges");
        })
        .always(enableUserActions);
}

function currentGroupId() {
    return $(dom.groupChooser).val();
}

function initAllLayers(blockDataAndTilerUrls) {
    if (tileLayer) {
        territoryMap.removeLayer(tileLayer);
        territoryMap.removeLayer(grid);
    }
    var blockDataList = blockDataAndTilerUrls.blockDataList,
        urls = blockDataAndTilerUrls.tilerUrls;
    tileLayer = mapModule.addTileLayer(territoryMap, urls.tile_url);
    grid = mapModule.addGridLayer(territoryMap, urls.grid_url);

    blockDataListForRevert = blockDataList;
    initSelectionLayer(blockDataList);
}

function initSelectionLayer(blockDataList) {
    if (selectionLayer) {
        territoryMap.removeLayer(selectionLayer);
        selectedBlockfaces = {};
    }
    selectionLayer = new SelectableBlockfaceLayer(territoryMap, grid, {
        onAdd: onBlockfaceMaybeAdd,
        onAdded: onBlockfaceAdded,
        onRemove: onBlockfaceRemove
    }).addTo(territoryMap);

    selectBlockfaces(blockDataList);
    hasUnsavedChanges = false;
}

function selectBlockfaces(blockDataList) {
    $.each(blockDataList, function (__, blockData) {
        if (!selectedBlockfaces[blockData.id]) {
            selectionLayer.addData({
                'type': 'Feature',
                'geometry': JSON.parse(blockData.geojson),
                'properties': {id: blockData.id}
            });
        }
    });
}

function deselectBlockfaces(blockDataList) {
    $.each(blockDataList, function (__, blockData) {
        var layer = selectedBlockfaces[blockData.id];
        if (layer) {
            selectionLayer.removeLayer(layer);
            delete selectedBlockfaces[blockData.id];
            hasUnsavedChanges = true;
        }
    });
}

function onBlockfaceAdded(feature, layer) {
    selectedBlockfaces[feature.properties.id] = layer;
    hasUnsavedChanges = true;
}

function onBlockfaceMaybeAdd(gridData) {
    var type = gridData.survey_type;
    if (type === 'available' || type === 'reserved') {
        return true;
    } else if (gridData.survey_type === 'unavailable') {
        if (gridData.turf_group_id) {
            var $option = $(dom.groupChooser + " option[value='" + gridData.turf_group_id + "']"),
                groupName = $option.text();
            toastr.error('That block is territory of ' + groupName);
        } else {
            toastr.error('That block is reserved by an individual');
        }
    } else {
        toastr.error('That block has already been surveyed');
    }
    return false;
}

function onBlockfaceRemove(feature) {
    delete selectedBlockfaces[feature.properties.id];
    hasUnsavedChanges = true;
    return true;
}

var drawer = null,
    willAddBlocks = null;

function drawAreaToAdd() { drawArea(true); }
function drawAreaToRemove() { drawArea(false); }

function drawArea(willAdd) {
    willAddBlocks = willAdd;
    toggleAreaControls();
    selectionLayer.clicksEnabled = false;
    drawer = new L.Draw.Polygon(territoryMap, {showArea: true});
    drawer.enable();
}

function stopDrawing() {
    toggleAreaControls();
    drawer.disable();
    selectionLayer.clicksEnabled = true;
}

function onAreaComplete(e) {
    stopDrawing();

    var polygonPoints = $.map(e.layer.getLatLngs(), function (p) {
            return [[p.lng, p.lat]];
        }),
        polygonString = JSON.stringify(polygonPoints),
        onSuccess = willAddBlocks ? selectBlockfaces : deselectBlockfaces;

    // Get blocks in polygon, then select or deselect them
    getGroupUnmappedTerritory(onSuccess, polygonString);
}

function toggleAreaControls() {
    $(dom.areaControls).toggleClass('hidden');
}

function revertTerritory() {
    if (okToProceed()) {
        initSelectionLayer(blockDataListForRevert);
    }
}

function saveTerritory() {
    disableUserActions();
    var blockface_ids = Object.keys(selectedBlockfaces);
    $.ajax({
        // Keep this URL in sync with "group_update_territory"
        // in src/nyc_trees/apps/users/urls/group.py
        url: '/group/' + currentGroupId() + '/update-territory/',
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(blockface_ids)
    })
        .done(initAllLayers)
        .fail(function () {
            toastr.error("Failed to save block edges");
        })
        .always(enableUserActions);
}

var $userActionControls = $([
        dom.groupChooser,
        dom.addAreaButton,
        dom.removeAreaButton,
        dom.revertButton,
        dom.saveButton
    ].join(','));

function disableUserActions() {
    $userActionControls.attr('disabled', 'disabled');
    if (selectionLayer) {
        territoryMap.removeLayer(selectionLayer);
    }
}

function enableUserActions() {
    $userActionControls.removeAttr('disabled');
    if (selectionLayer) {
        territoryMap.addLayer(selectionLayer);
    }
}
