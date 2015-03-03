"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    mapUtil = require('./lib/mapUtil'),
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

$(dom.selectGroup).on('change', updateTileLayer);

function updateTileLayer(e) {
    var group_id = $(e.target).val(),
        query = 'group=' + group_id;
    if (tileLayer) {
        territoryMap.removeLayer(tileLayer);
        territoryMap.removeLayer(grid);
        territoryMap.removeLayer(selectedLayer);
    }
    tileLayer = mapModule.addTileLayer(territoryMap, query);
    grid = mapModule.addGridLayer(territoryMap, query);
    selectedLayer = new SelectableBlockfaceLayer(territoryMap, grid, {
        onAdd: function (gridData) {
            selectedLayer.clearLayers();
            return true;
        }
    });
    territoryMap.addLayer(selectedLayer);
}
