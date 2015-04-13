"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    mapUtil = require('./lib/mapUtil'),
    zoom = require('./lib/mapUtil').ZOOM,
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer'),
    BlockfaceLayer = require('./lib/BlockfaceLayer'),
    SavedState = require('./lib/SavedState'),

    attrs = {
        blockfaceId: 'data-blockface-id',
        blockfaceStatus: 'data-blockface-status',
        blockfaceAction: 'data-blockface-action'
    },

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
        unavailableBlockfaceModal: '#unavailable-blockface-modal',

        startSection: '#reservations-start',
        addRemoveBtn: '#reservations-add-remove',

        cartActionBar: '#reservations-cart-action',
        cartHelpText: '#reservations-help-text',
        cartFinishSection: '#reservations-finish-section',

        blockActionBar: '#reservations-blockface-action',
        blockActionPopupContainer: '#reservations-blockface-popup-container',
        blockActionBarClose: '#close-blockface-action',

        popupTemplate: '#reservations-blockface-popup-template',
        popupBlockfaceId: '[' + attrs.blockfaceId + ']',
        popupBlockfaceStatus: '[' + attrs.blockfaceStatus + ']',
        popupAction: '[' + attrs.blockfaceAction + ']',
    },

    actions = {
        remove: 'Remove',
        add: 'Add to Cart'
    },

    currentlyReservedIds = [];

require('./lib/mapHelp');

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
    blockfaceLayers = {},

    grid = mapModule.addGridLayer(reservationMap);

var progress = new SavedState({
    key: 'reserve-blockfaces',
    validate: function(state) {
        if (!$.isPlainObject(state.selections)) {
            throw new Error('Expected `state.selections` to contain blockfaces');
        }
    }
});

var selectedLayer = new SelectableBlockfaceLayer(reservationMap, grid, {
    onAdd: function(gridData, __, latlng) {
        onAddRemove();
        if (selectedBlockfacesCount >= blockfaceLimit) {
            $(dom.limitReachedModal).modal('show');
        } else if (gridData.restriction === "none") {
            selectedLayer.clearLayers();
            showPopup(gridData.id, latlng, 'Available', actions.add);

            return true;
        }
        return false;
    },

    onRemove: function(feature) {
        reservationMap.closePopup();
        return true;
    }
});

var reservedLayer = new BlockfaceLayer(reservationMap, {
    color: '#CE2029',
    onEachFeature: function(feature, layer) {
        layer.on('click', function(e) {
            onAddRemove();
            showPopup(feature.properties.id, e.latlng, 'Expires ' + feature.properties.expires_at, actions.remove);
            blockfaceLayers[feature.properties.id] = layer;
            selectedLayer.addData(feature);
        });
    }
});

var cartLayer = new BlockfaceLayer(reservationMap, {
    color: '#FF69B4',
    onEachFeature: function(feature, layer) {
        layer.on('click', function(e) {
            onAddRemove();
            showPopup(feature.properties.id, e.latlng, 'In Cart', actions.remove);
            blockfaceLayers[feature.properties.id] = layer;
            selectedLayer.addData(feature);
        });
    }
});

// Keep this URL in sync with src/nyc_trees/apps/survey/urls/blockface.py
$.getJSON("/blockedge/reserved-blockedges.json", function(data) {
    $.each(data, function(__, blockface) {
        selectedBlockfaces[blockface.properties.id] = blockface;
        reservedLayer.addData(blockface);
        currentlyReservedIds.push(blockface.properties.id);
    });
});

function showPopup(blockfaceId, latlng, status, action) {
    var $popup = $($(dom.popupTemplate).html());

    $popup.find(dom.popupBlockfaceStatus).html(status);

    // Bit of a cludge here, 'id' and 'action' are both on the same element,
    // Calling '.html(...)' for action last ensures the correct text is present
    $popup.find(dom.popupBlockfaceId).attr(attrs.blockfaceId, blockfaceId).html(blockfaceId);
    $popup.find(dom.popupAction).attr(attrs.blockfaceAction, action).html(action);

    // We add the blockface popup in 2 places, as a leaflet popup and as an
    // action bar item
    // CSS media queries will hide one or the other depending on screen size
    L.popup({className: 'reservation-leaflet-popup'})
        .setLatLng(latlng)
        .setContent($popup[0])
        .openOn(reservationMap);

    $(dom.blockActionBar).addClass('active');
    $(dom.blockActionPopupContainer).html($popup.clone());
    $(dom.cartActionBar).removeClass('active');
}

$(dom.blockActionBarClose).on('click', closeActionbar);

function closeActionbar() {
    $(dom.blockActionBar).removeClass('active');
    $(dom.cartActionBar).addClass('active');
    selectedLayer.clearLayers();
}

reservationMap.on('popupclose', function() {
    selectedLayer.clearLayers();
    closeActionbar();
});

$('body').on('click', dom.popupAction, function(e) {
    var $elem = $(e.currentTarget),
        action = $elem.text(),
        blockfaceId = $elem.attr(attrs.blockfaceId);

    if (action === actions.add) {
        addToCart(blockfaceId);
    } else if (action === actions.remove) {
        removeFromCart(blockfaceId);
    }

    selectedLayer.clearLayers();
    reservationMap.closePopup();
    closeActionbar();
});

function addToCart(id) {
    $(dom.cartHelpText).addClass('hidden');
    $(dom.cartFinishSection).removeClass('hidden');

    selectedBlockfaces[id] = null;
    selectedBlockfacesCount++;
    $current.text(selectedBlockfacesCount);

    updateForm();

    cartLayer.addData(selectedLayer.getLayers()[0].feature);
    reservedLayer.removeLayer(blockfaceLayers[id]);
    delete blockfaceLayers[id];
}

function removeFromCart(id) {
    $(dom.cartHelpText).addClass('hidden');
    $(dom.cartFinishSection).removeClass('hidden');

    if (selectedBlockfacesCount > 0) {
        selectedBlockfacesCount--;
        $current.text(selectedBlockfacesCount);
    }
    delete selectedBlockfaces[id];
    updateForm();

    cartLayer.removeLayer(blockfaceLayers[id]);
    reservedLayer.removeLayer(blockfaceLayers[id]);
    delete blockfaceLayers[id];
}

function updateForm() {
    var ids = Object.keys(selectedBlockfaces);
    // Check if the blockfaces in the cart are identical to those already
    // reserved, and enable the button if they are different

    if ( ! arrayEquals(ids, currentlyReservedIds)) {
        $hiddenInput.val(ids.join());
        $finishButton.prop('disabled', false);
    } else {
        $finishButton.prop('disabled', true);
    }
}

function arrayEquals(a, b) {
    // compare lengths - can save a lot of time
    if (a.length != b.length) {
        return false;
    }
    a.sort();
    b.sort();

    for (var i = 0, l=a.length; i < l; i++) {
        if (a[i] != b[i]) {
            return false;
        }
    }
    return true;
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

reservationMap.addLayer(cartLayer);
reservationMap.addLayer(reservedLayer);
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

// Zoom the map to fit a blockface ID pased in the URL hash
var blockfaceId = mapUtil.getBlockfaceIdFromUrl();
mapUtil.fetchBlockface(blockfaceId).done(function(blockface) {
    selectedLayer.addBlockface(blockface);
});

$(dom.addRemoveBtn).on('click', onAddRemove);

function onAddRemove() {
    $(dom.startSection).addClass('hidden');
    $(dom.cartActionBar).removeClass('hidden').addClass('active');
}
