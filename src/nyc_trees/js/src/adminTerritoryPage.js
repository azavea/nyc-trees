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
        selectGroup: '#select-group',
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
    selectedLayer = null,
    selectedBlockfaces = {};

$(document).ready(showDataForChosenGroup);
$(dom.selectGroup).on('change', showDataForChosenGroup);

$(dom.addAreaButton).click(drawAreaToAdd);
$(dom.removeAreaButton).click(drawAreaToRemove);
$(dom.cancelAreaButton).click(stopDrawing);

territoryMap.on('draw:created', onAreaComplete);

$(dom.revertButton).click(revertTerritory);
$(dom.saveButton).click(saveTerritory);

function showDataForChosenGroup() {
    var query = 'group=' + currentGroupId();
    if (tileLayer) {
        territoryMap.removeLayer(tileLayer);
        territoryMap.removeLayer(grid);
        territoryMap.removeLayer(selectedLayer);
        selectedBlockfaces = {};
    }
    tileLayer = mapModule.addTileLayer(territoryMap, query);
    grid = mapModule.addGridLayer(territoryMap, query);
    selectBlockfacesInGroupTerritory();
}

function selectBlockfacesInGroupTerritory() {
    if (selectedLayer ) {
        territoryMap.removeLayer(selectedLayer);
        selectedBlockfaces = {};
    }
    selectedLayer = new SelectableBlockfaceLayer(territoryMap, grid, {
        onAdd: onBlockfaceMaybeAdd,
        onAdded: onBlockfaceAdded,
        onRemove: onBlockfaceRemove
    }).addTo(territoryMap);

    getUnmappedTerritory(currentGroupId())
        .done(addBlockfacesToSelection);
}

function currentGroupId() {
    return $(dom.selectGroup).val();
}

function getUnmappedTerritory(groupId, polygon) {
    var promise = $.ajax({
        // Keep this URL in sync with "group_territory_geojson"
        // in src/nyc_trees/apps/users/urls/group.py
        url: '/group/' + groupId + '/territory.json/',
        type: 'POST',
        dataType: 'json',
        data: polygon,
        error: function () {
            toastr.error("Failed to retrieve blockfaces");
        }
    });
    return promise;
}

function addBlockfacesToSelection(blockDataList) {
    $.each(blockDataList, function (__, blockData) {
        if (!selectedBlockfaces[blockData.id]) {
            selectedLayer.addData({
                'type': 'Feature',
                'geometry': JSON.parse(blockData.geojson),
                'properties': {id: blockData.id}
            });
        }
    });
}

function removeBlockfacesFromSelection(blockDataList) {
    $.each(blockDataList, function (__, blockData) {
        var layer = selectedBlockfaces[blockData.id];
        if (layer) {
            selectedLayer.removeLayer(layer);
            delete selectedBlockfaces[blockData.id];
        }
    });
}

function onBlockfaceAdded(feature, layer) {
    selectedBlockfaces[feature.properties.id] = layer;
}

function onBlockfaceMaybeAdd(gridData) {
    var type = gridData.survey_type;
    if (type === 'available' || type === 'reserved') {
        return true;
    } else if (gridData.survey_type === 'unavailable') {
        if (gridData.turf_group_id) {
            var $option = $(dom.selectGroup + " option[value='" + gridData.turf_group_id + "']"),
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
    return true;
}

var drawer = null,
    willAddBlocks = null;

function drawAreaToAdd() { drawArea(true); }
function drawAreaToRemove() { drawArea(false); }

function drawArea(willAdd) {
    willAddBlocks = willAdd;
    toggleAreaControls();
    selectedLayer.clicksEnabled = false;
    drawer = new L.Draw.Polygon(territoryMap, {showArea: true});
    drawer.enable();
}

function stopDrawing() {
    toggleAreaControls();
    drawer.disable();
    selectedLayer.clicksEnabled = true;
}

function onAreaComplete(e) {
    stopDrawing();

    var polygonPoints = $.map(e.layer.getLatLngs(), function (p) {
            return [[p.lng, p.lat]];
        }),
        polygonString = JSON.stringify(polygonPoints);

    getUnmappedTerritory(currentGroupId(), polygonString)
        .done(willAddBlocks ? addBlockfacesToSelection : removeBlockfacesFromSelection);
}

function toggleAreaControls() {
    $(dom.areaControls).toggleClass('hidden');
}

function revertTerritory() {
    selectBlockfacesInGroupTerritory();
}

function saveTerritory() {
}
