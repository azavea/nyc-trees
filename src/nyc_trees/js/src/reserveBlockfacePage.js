"use strict";

var mapModule = require('./map'),
    zoom = require('./mapUtil').zoom,
    selectableBlockfaceLayer = require('./selectableBlockfaceLayer'),
    L = require('leaflet'),
    $ = require('jquery'),
    Storage = require('./lib/storage'),

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

var progress = new Storage({
    key: 'reserve-blockfaces',
    getState: function() {
        return {
            selections: selectedBlockfaces
        };
    },
    validate: function(state) {
        if (!$.isPlainObject(state.selections)) {
            throw new Error('Expected `state.selections` to contain blockfaces');
        }
    }
});

var blockfaceLayer = selectableBlockfaceLayer.create({
    map: reservationMap,
    grid: grid,

    onAdd: function(gridData) {
        if (selectedBlockfacesCount < blockfaceLimit && gridData.restriction === 'none') {
            selectedBlockfaces[gridData.id] = gridData;
            selectedBlockfacesCount++;
            $current.text(selectedBlockfacesCount);

            progress.save();
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

        progress.save();
        return true;
    }
});

// Load any existing data.
var state = progress.load();
if (state) {
    $.each(state.selections, function(id, data) {
        blockfaceLayer.addBlockface(data);
    });
}
