"use strict";

var $ = require('jquery'),
    zoom = require('./lib/mapUtil').ZOOM,
    L = require('leaflet'),
    mapModule = require('./map'),
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer');

require('./lib/mapHelp');

var progressMap = mapModule.create({
        geolocation: true,
        legend: true,
        search: true
    }),
    tileLayer = null,
    geojsonLayer = null,

    dom = {
        modeDropdown: '.dropdown',
        modeButton: '.btn',
        modeChoice: '.dropdown li a',
        legendEntries: '[data-mode]',
        actionBar: '#action-bar'
    },
    $actionBar = $(dom.actionBar),
    $mode = null,

    selectedLayer = new SelectableBlockfaceLayer(progressMap, null, {
        onAdd: function() { return true; }, // Always try and fetch the feature
        onAdded: function(feature, layer) {
            selectedLayer.clearLayers();

            // Note: this must be kept in sync with
            // src/nyc_trees/apps/survey/urls/blockface.py
            var url = '/blockedge/' + feature.properties.id + '/progress-page-blockedge-popup/';

            $actionBar.load(url);
            $('body').addClass('actionbar-triggered');
            return true;
        }
    });

$(dom.modeChoice).click(onModeChanged);

// The progress page does not have a grid, so we set a pointer
// cursor to indicate that a click/tap will do something no
// matter where you click/tap.
$('.leaflet-container').css('cursor', 'pointer');


// Maximum zoom levels for aggregate layers
var zoomMaxes = {
    borough: 12,
    nta: 15
};

var boroughLayer = mapModule.addTileLayer(progressMap, {
    url: '//33.33.33.20/1430516442/nyc_trees/borough_progress/{z}/{x}/{y}.png',
    minZoom: 1,
    maxZoom: zoomMaxes.borough
});

var ntaLayer = mapModule.addTileLayer(progressMap, {
    url: '//33.33.33.20/1430516442/nyc_trees/nta_progress/{z}/{x}/{y}.png',
    minZoom: zoomMaxes.borough + 1,
    maxZoom: zoomMaxes.nta
});

// Work around https://github.com/Leaflet/Leaflet/issues/1905
progressMap.on('zoomend', function(e) {
    var zoom = progressMap.getZoom();
        if (zoom > zoomMaxes.borough) {
        boroughLayer._clearBgBuffer();
    }
    if (zoom < (zoomMaxes.borough + 1) || zoom > zoomMaxes.nta) {
        ntaLayer._clearBgBuffer();
    }
    if (zoom < (zoomMaxes.nta + 1) && tileLayer) {
        tileLayer._clearBgBuffer();
    }
});

loadLayers($(dom.modeChoice).first());

progressMap.addLayer(selectedLayer);

function onModeChanged(e) {
    e.preventDefault();
    if ($mode !== null && $mode[0] === e.currentTarget) {
        return;
    }
    $mode = $(e.currentTarget);
    if ($mode.hasClass('js-my-progress') && !$mode.attr('href')) {
        return;
    }

    // Show chosen mode on dropdown button
    $mode.parents(dom.modeDropdown).find(dom.modeButton).text($mode.text());

    // Show appropriate legend entries
    var mode = $mode.attr('href').slice(1);  // strip leading #
    $(dom.legendEntries).addClass('hidden');
    $('[data-mode=' + mode + ']').removeClass('hidden');

    loadLayers($mode);
}

function loadLayers($mode) {
    var tileUrl = $mode.data('tile-url'),
        geojsonUrl = $mode.data('geojson-url'),
        bounds = $mode.data('bounds');

    // Clear action bar
    $actionBar.empty();
    $('body').removeClass('actionbar-triggered');
    selectedLayer.clearLayers();

    // Replace layers
    if (tileLayer) {
        progressMap.removeLayer(tileLayer);
    }
    if (geojsonLayer) {
        progressMap.removeLayer(geojsonLayer);
    }

    if (tileUrl) {
        addLayers(bounds, tileUrl, {minZoom: zoomMaxes.nta + 1, maxZoom: zoom.MAX});
        selectedLayer.clicksEnabled = true;
    } else {
        selectedLayer.clicksEnabled = false;
    }

    if (geojsonUrl) {
        $.getJSON(geojsonUrl, function(geojson) {
            geojsonLayer = L.geoJson(geojson, {
                style: function() {
                    return {
                        color: '#36b5db',
                        weight: 3
                    };
                },
                onEachFeature: function(feature, layer) {
                    layer.on('click', function showGroupBlockfaces() {
                        progressMap.removeLayer(tileLayer);

                        var p = feature.properties;
                        addLayers(p.bounds, p.tileUrl);

                        $actionBar.load(p.popupUrl);
                        $('body').addClass('actionbar-triggered');
                    });
                }
            });
            geojsonLayer.addTo(progressMap);
        });
    }
}

function addLayers(bounds, tileUrl, options) {
    // Add layer to map after zoom animation completes.
    // (Otherwise spurious tile requests will be issued at the old zoom level.)
    mapModule.fitBounds(progressMap, bounds).then(function() {
        tileLayer = mapModule.addTileLayer(progressMap, {
            url: tileUrl,
            minZoom: options.minZoom,
            maxZoom: options.maxZoom
        });
    });
}
