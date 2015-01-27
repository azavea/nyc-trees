"use strict";

var mapModule = require('./map'),
    zoom = require('./mapUtil').zoom,
    selectableBlockfaceLayer = require('./selectableBlockfaceLayer'),
    L = require('leaflet'),
    $ = require('jquery'),

    dom = {
        currentReservations: "#current-reservations",
        totalReservations: "#total-reservations"
    };

// Extends the leaflet object
require('leaflet-utfgrid');

var reservationMap = mapModule.create({
    geolocation: true,
    legend: true,
    search: true
});

L.tileLayer(config.urls.layers.reservable.tiles, {
    maxZoom: zoom.MAX
}).addTo(reservationMap);

var $current = $(dom.currentReservations),
    selectedBlockfacesCount = +($current.text()),
    blockfaceLimit = +($(dom.totalReservations).text()),
    selectedBlockfaces = {},

    grid = L.utfGrid(config.urls.layers.reservable.grids, {
        maxZoom: zoom.MAX,
        useJsonP: false
    });


selectableBlockfaceLayer.create({
    map: reservationMap,
    grid: grid,

    onAdd: function(gridData) {
        if (selectedBlockfacesCount < blockfaceLimit && gridData.restriction === 'none') {
            selectedBlockfaces[gridData.id] = gridData;
            selectedBlockfacesCount++;
            $current.text(selectedBlockfacesCount);

            return true;
        }

        return false;
    },

    onRemove: function(feature) {
        if (selectedBlockfacesCount > 0) {
            selectedBlockfacesCount--;
            $current.text(selectedBlockfacesCount);
        }
        delete selectedBlockfaces[feature.properties.id];

        return true;
    }
});
