"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    toastr = require('toastr'),
    mapModule = require('./map'),
    zoom = require('./mapUtil').zoom,
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer'),

    dom = {
        actionBar: '#reserve-blockface-action-bar',
        modalTemplate: '#cancel-reservation-template',
        modalContainer: '#reservation-modal',
        cancelLink: '[data-action="cancel-reservation"]',
    },

    $actionBar = $(dom.actionBar),
    $modalContainer = $(dom.modalContainer);

// Extends the leaflet object
require('leaflet-utfgrid');

var reservationMap = mapModule.create({
    geolocation: true,
    legend: true,
    search: true
});

var tileLayer = mapModule.addTileLayer(reservationMap),
    grid = mapModule.addGridLayer(reservationMap),

    selectedLayer = new SelectableBlockfaceLayer(reservationMap, grid, {
        onAdd: function(gridData) {
            selectedLayer.clearLayers();

            // Note: this must be kept in sync with
            // src/nyc_trees/apps/survey/urls/blockface.py
            $actionBar.load('/blockface/' + gridData.id + '/reservation-popup/', function() {
                var modalContent = $actionBar.find(dom.modalTemplate).html();
                $modalContainer.html(modalContent);
            });
            return true;
        }
    });

var hash = window.location.hash;

reservationMap.addLayer(grid);
reservationMap.addLayer(selectedLayer);

$modalContainer.on('click', dom.cancelLink, function(e) {
    var $button = $(e.currentTarget);
    e.preventDefault();

    $button.prop('disabled', true);

    $.getJSON($button.attr('data-url'), function(layer) {
        tileLayer.setUrl(layer.tile_url);

        // utfGrid does not expose a setUrl method
        grid._url = layer.grid_url;
        grid._cache = {};
        grid._update();

        $actionBar.empty();
        selectedLayer.clearLayers();

        $modalContainer.modal('hide');
    }).fail(function() {
        toastr.error('Could not cancel your reservation, please try again later');
    }).always(function() {
        $button.prop('disabled', false);
    });
});


// Zoom the map to fit a blockface ID pased in the URL hash
// Assumes that the hash contains only a blockface ID
// NOTE: This has a hard coded url that must be kept in sync with
// apps/survey/urls/blockface.py
if (hash) {
    $.getJSON('/blockface/' + hash.substring(1) + '/', function(blockface) {
        var e = blockface.extent,
            sw = L.latLng(e[1], e[0]),
            ne = L.latLng(e[3], e[2]),
            bounds = L.latLngBounds(sw, ne);
        reservationMap.fitBounds(bounds);
    });
}
