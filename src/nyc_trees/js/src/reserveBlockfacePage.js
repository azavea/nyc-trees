"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    zoom = require('./lib/mapUtil').ZOOM,
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer'),
    SavedState = require('./lib/SavedState'),

    dom = {
        modals: '.modal',
        currentReservations: "#current-reservations",
        totalReservations: "#total-reservations",
        finishReservations: "#finish-reservations",
        hiddenInput: "#reservation-ids",
        requestAccessButton: '[data-action="request-access"]',
        limitReachedModal: '#limit-reached-modal',
        alreadyReservedModal: '#already-reserved-modal',
        requestAccessModal: '#request-access-modal',
        requestAccessCompleteModal: '#request-access-complete-modal',
        requestAccessFailModal: '#request-access-fail-modal',
        unavailableBlockfaceModal: '#unavailable-blockface-modal'
    };

// Extends the leaflet object
require('leaflet-utfgrid');

var reservationMap = mapModule.create({
    geolocation: true,
    legend: true,
    search: true
});

mapModule.addTileLayer(reservationMap);

var $current = $(dom.currentReservations),
    $hiddenInput = $(dom.hiddenInput),
    $finishButton = $(dom.finishReservations),

    selectedBlockfacesCount = +($current.text()),
    blockfaceLimit = +($(dom.totalReservations).text()),
    selectedBlockfaces = {},

    grid = mapModule.addGridLayer(reservationMap);

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
        if (selectedBlockfacesCount >= blockfaceLimit) {
            $(dom.limitReachedModal).modal('show');
        } else if (gridData.restriction === 'none') {
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
    if (e.data.restriction === 'group_territory') {
        $(dom.requestAccessModal)
            .find(dom.requestAccessButton)
            .data('group-slug', e.data.group_slug);
        $(dom.requestAccessModal).modal('show');
    } else if (e.data.restriction === 'reserved') {
        $(dom.alreadyReservedModal).modal('show');
    } else if (e.data.restriction !== 'none') {
        $(dom.unavailableBlockfaceModal).modal('show');
    }
});

reservationMap.addLayer(selectedLayer);

$(dom.requestAccessModal).on('click', dom.requestAccessButton, function() {
    var groupSlug = $(dom.requestAccessButton).data('group-slug');
    $(dom.modals).modal('hide');
    $.ajax({
            // Keep this URL in sync with "request_mapper_status"
            // in src/nyc_trees/apps/users/urls/group.py
            url: '/group/' + groupSlug + '/request-trusted-mapper-status/',
            type: 'POST'
        })
        .done(function() {
            $(dom.requestAccessCompleteModal).modal('show');
        })
        .fail(function() {
            $(dom.requestAccessFailModal).modal('show');
        });
});

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
