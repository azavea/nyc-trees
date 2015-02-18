"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer');

// Extends the leaflet object
require('leaflet-utfgrid');

var blockfaceMap = mapModule.create({
    legend: true,
    search: true
});

var tileLayer = mapModule.addTileLayer(blockfaceMap),
    grid = mapModule.addGridLayer(blockfaceMap),

    selectedLayer = new SelectableBlockfaceLayer(blockfaceMap, grid, {
        onAdd: function(gridData) {
            selectedLayer.clearLayers();
            return true;
        }
    });

blockfaceMap.addLayer(grid);
blockfaceMap.addLayer(selectedLayer);
