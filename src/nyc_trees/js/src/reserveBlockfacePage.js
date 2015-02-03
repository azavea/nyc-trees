"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    toastr = require('toastr'),
    mapModule = require('./map'),
    zoom = require('./mapUtil').zoom,
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer'),
    SavedState = require('./lib/SavedState'),

    dom = {
        currentReservations: "#current-reservations",
        totalReservations: "#total-reservations",
        finishReservations: "#finish-reservations",
        hiddenInput: "#reservation-ids"
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
    $hiddenInput = $(dom.hiddenInput),
    $finishButton = $(dom.finishReservations),

    selectedBlockfacesCount = +($current.text()),
    blockfaceLimit = +($(dom.totalReservations).text()),
    selectedBlockfaces = {},

    grid = L.utfGrid(config.urls.layers.reservable.grids, {
        maxZoom: zoom.MAX,
        useJsonP: false
    });

var progress = new SavedState({
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

var selectedLayer = new SelectableBlockfaceLayer(reservationMap, grid, {
    onAdd: function(gridData) {
        if (selectedBlockfacesCount < blockfaceLimit &&
                gridData.restriction === 'none') {
            selectedBlockfaces[gridData.id] = gridData;
            selectedBlockfacesCount++;
            $current.text(selectedBlockfacesCount);

            updateForm();

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
        updateForm();

        progress.save();
        return true;
    }
});

function updateForm() {
    var ids = Object.keys(selectedBlockfaces);
    if (ids.length > 0) {
        $hiddenInput.val(ids.join());
        $finishButton.prop('disabled', false);
    } else {
        $finishButton.prop('disabled', true);
    }
}

grid.on('click', function(e) {
    if (!e.data) {
        return;
    }
    if (selectedBlockfacesCount >= blockfaceLimit) {
        toastr.error('You have reached your reservation limit');
    } else if (e.data.restriction !== 'none') {
        toastr.error('The blockface you selected is not available');
    }
});

reservationMap.addLayer(grid);
reservationMap.addLayer(selectedLayer);

// Load any existing data.
var state = progress.load();
if (state) {
    $.each(state.selections, function(id, data) {
        selectedLayer.addBlockface(data);
    });
    try {
        // Zoom to extent of selected blockface reservations.
        reservationMap.fitBounds(selectedLayer.getBounds());
    } catch (ex) {
        // Ignore Leaflet fitBounds error when there are no selections.
    }
}
