"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    mapUtil = require('./lib/mapUtil'),
    toastr = require('toastr'),
    zoom = require('./lib/mapUtil').ZOOM,
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer');

// Extends the leaflet object
require('leaflet-utfgrid');

var dom = {
        selectGroup: '#select-group',
        actionBar: '#action-bar'
    },
    $actionBar = $(dom.actionBar),

    territoryMap = mapModule.create({
        legend: true,
        search: true
    }),
    tileLayer = null,
    grid = null,
    selectedLayer = null;

$(document).ready(showDataForChosenGroup);
$(dom.selectGroup).on('change', showDataForChosenGroup);

function showDataForChosenGroup() {
    var groupId = $(dom.selectGroup).val(),
        query = 'group=' + groupId;
    if (tileLayer) {
        territoryMap.removeLayer(tileLayer);
        territoryMap.removeLayer(grid);
        territoryMap.removeLayer(selectedLayer);
    }
    tileLayer = mapModule.addTileLayer(territoryMap, query);
    grid = mapModule.addGridLayer(territoryMap, query);

    $.ajax({
        // Keep this URL in sync with "group_territory_geojson"
        // in src/nyc_trees/apps/users/urls/group.py
        url: '/group/' + groupId + '/territory.json/',
        type: 'GET',
        success: initBlockfaceLayer,
        error: function () {
            window.alert("Unable to load blockfaces for this group");
        }
    });
}

function initBlockfaceLayer(data) {
    selectedLayer = new SelectableBlockfaceLayer(territoryMap, grid, {
        onAdd: onBlockfaceAdd,
        onRemove: onBlockfaceRemove
    });
    // Add group's unmapped territory to selectedLayer
    $.each(data, function(__, blockData) {
        selectedLayer.addData({
            'type': 'Feature',
            'geometry': JSON.parse(blockData.geojson),
            'properties': {id: blockData.id}
        });
    });
    territoryMap.addLayer(selectedLayer);
}

function onBlockfaceAdd(gridData) {
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
    return true;
}