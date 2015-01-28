"use strict";

var MapModule = require('./map'),
    zoom = require('./mapUtil').zoom,
    selectableBlockfaceLayer = require('./selectableBlockfaceLayer'),
    L = require('leaflet'),
    $ = require('jquery'),

    dom = {
        actionBar: '#reserve-blockface-action-bar'
    },

    $actionBar = $(dom.actionBar);

// Extends the leaflet object
require('leaflet-utfgrid');

var reservationMap = MapModule.create({
    geolocation: true,
    legend: true,
    search: true
});

L.tileLayer(config.urls.layers.reservations.tiles, {
    maxZoom: zoom.MAX
}).addTo(reservationMap);

var grid = L.utfGrid(config.urls.layers.reservations.grids, {
        maxZoom: zoom.MAX,
        useJsonP: false
    }),

    selectedLayer = selectableBlockfaceLayer.create({
        map: reservationMap,
        grid: grid,

        onAdd: function(gridData) {
            selectedLayer.clearLayers();

            // Note: this must be kept in sync with
            // src/nyc_trees/apps/survey/urls/blockface.py
            $actionBar.load('/blockface/' + gridData.id + '/reservation-popup/');
            return true;
        }
    });
