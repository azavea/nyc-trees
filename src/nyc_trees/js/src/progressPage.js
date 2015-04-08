"use strict";

var $ = require('jquery'),
    zoom = require('./lib/mapUtil').ZOOM,
    L = require('leaflet'),
    mapModule = require('./map'),
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer');

require('./lib/mapHelp');

// Extends the leaflet object
require('leaflet-utfgrid');

var progressMap = mapModule.create({
        geolocation: true,
        legend: true,
        search: true
    }),
    tileLayer = null,
    grid = null,
    selectedLayer = null,

    dom = {
        modeDropdown: '.dropdown',
        modeButton: '.btn',
        modeChoice: '.dropdown li a',
        legendEntries: '.entry',
        actionBar: '#action-bar'
    },
    $actionBar = $(dom.actionBar);

$(dom.modeChoice).click(onModeChanged);

$(dom.modeChoice).first().trigger('click');

function onModeChanged(e) {
    var $mode = $(e.currentTarget),
        tileUrl = $mode.data('tile-url'),
        gridUrl = $mode.data('grid-url'),
        bounds = $mode.data('bounds');

    // Shown chosen mode on dropdown button
    $mode.parents(dom.modeDropdown).find(dom.modeButton).text($mode.text());

    // Show appropriate legend entries
    var mode = $mode.attr('href').slice(1);  // strip leading #
    $(dom.legendEntries).hide();
    $('[data-mode=' + mode + ']').show();

    // Clear action bar
    $actionBar.empty();

    // Replace layers
    if (tileLayer) {
        progressMap.removeLayer(tileLayer);
        progressMap.removeLayer(grid);
        progressMap.removeLayer(selectedLayer);
    }
    if (tileUrl) {
        tileLayer = mapModule.addTileLayer(progressMap, tileUrl);

        grid = mapModule.addGridLayer(progressMap, gridUrl);

        selectedLayer = new SelectableBlockfaceLayer(progressMap, grid, {
            onAdd: function(gridData) {
                selectedLayer.clearLayers();

                // Note: this must be kept in sync with
                // src/nyc_trees/apps/survey/urls/blockface.py
                var url =
                        '/blockface/' + gridData.id +
                        '/progress-page-blockface-popup/?survey_type=' + gridData.survey_type;
                if (gridData.group_id) {
                    url += '&group_id=' + gridData.group_id;
                }
                $actionBar.load(url);
                return true;
            }
        });
        progressMap.addLayer(selectedLayer);

        if (bounds) {
            mapModule.fitBounds(progressMap, bounds);
        }
    }
}