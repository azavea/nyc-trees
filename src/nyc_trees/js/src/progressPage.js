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
        search: true,
        // Using a separate layer for labels interferes with the neighborhood and borough layers
        withLabels: true
    }),
    tileLayer = null,
    neighborhoodTileLayer=null,
    boroughTileLayer = null,
    geojsonLayer = null,

    dom = {
        modeDropdown: '.dropdown',
        modeButton: '.btn',
        modeChoice: '.dropdown li a',
        legendEntries: '[data-mode]',
        actionBar: '#action-bar'
    },
    $actionBar = $(dom.actionBar),
    $mode = $(dom.modeChoice).first(),

    // Maximum zoom levels for aggregate layers
    zoomMaxes = {
        borough: 12,
        neighborhood: 15
    },
    selectedLayer = new SelectableBlockfaceLayer(progressMap, null, {
        onAdd: function() {
            if ($mode !== null && $mode.data('tile-url-neighborhood')) {
                // If this mode has a neighborhood layer, only allow clicks
                // when we are zoomed in past it
                return progressMap.getZoom() > zoomMaxes.neighborhood;
            }
            return true;
        },
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

loadLayers($mode);

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

    changeLegendEntries();

    // Show chosen mode on dropdown button
    $mode.parents(dom.modeDropdown).find(dom.modeButton).text($mode.text());

    loadLayers($mode);
}

function changeLegendEntries() {
    // Show appropriate legend entries
    var mode = $mode.attr('href').slice(1);  // strip leading #

    // Show different legend entries depending on zoom level if appropriate for
    // this mode
    if ($mode.data('tile-url-neighborhood') && progressMap.getZoom() <= zoomMaxes.neighborhood) {
        mode = mode + '-percent';
    }
    $(dom.legendEntries).addClass('hidden');
    $('[data-mode=' + mode + ']').removeClass('hidden');
}

function clearSelection() {
    // Clear action bar
    $actionBar.empty();
    $('body').removeClass('actionbar-triggered');
    // Clear selected blockface
    selectedLayer.clearLayers();
}

function loadLayers($mode) {
    var tileUrl = $mode.data('tile-url'),
        neighborhoodTileUrl = $mode.data('tile-url-neighborhood'),
        boroughTileUrl = $mode.data('tile-url-borough'),
        geojsonUrl = $mode.data('geojson-url'),
        bounds = $mode.data('bounds');

    progressMap.off('zoomend', fixZoomLayerSwitch);
    progressMap.off('zoomend', changeLegendEntries);

    // Replace layers
    $.each([tileLayer, geojsonLayer, neighborhoodTileLayer, boroughTileLayer], function(_, layer) {
        if (layer) {
            progressMap.removeLayer(layer);
        }
    });
    clearSelection();

    if (tileUrl) {
        addLayers(bounds, tileUrl, neighborhoodTileUrl, boroughTileUrl);
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

function addLayers(bounds, tileUrl, neighborhoodTileUrl, boroughTileUrl) {
    // Add layer to map after zoom animation completes.
    // (Otherwise spurious tile requests will be issued at the old zoom level.)
    mapModule.fitBounds(progressMap, bounds).then(function() {
        if (neighborhoodTileUrl || boroughTileUrl) {
            tileLayer = mapModule.addTileLayer(progressMap, {
                url: tileUrl,
                minZoom: zoomMaxes.neighborhood + 1,
                maxZoom: zoom.MAX
            });

            boroughTileLayer = mapModule.addTileLayer(progressMap, {
                url: boroughTileUrl,
                minZoom: 1,
                maxZoom: zoomMaxes.borough
            });

            neighborhoodTileLayer = mapModule.addTileLayer(progressMap, {
                url: neighborhoodTileUrl,
                minZoom: zoomMaxes.borough + 1,
                maxZoom: zoomMaxes.neighborhood
            });

            progressMap.on('zoomend', fixZoomLayerSwitch);
            progressMap.on('zoomend', changeLegendEntries);
        } else {
            tileLayer = mapModule.addTileLayer(progressMap, {
                url: tileUrl
            });
        }
    });
}

// Work around https://github.com/Leaflet/Leaflet/issues/1905
function fixZoomLayerSwitch(e) {
    var zoom = progressMap.getZoom();
    if (zoom > zoomMaxes.borough) {
        boroughTileLayer._clearBgBuffer();
    }
    if (zoom < (zoomMaxes.borough + 1) || zoom > zoomMaxes.neighborhood) {
        neighborhoodTileLayer._clearBgBuffer();
    }
    if (zoom < (zoomMaxes.neighborhood + 1)) {
        clearSelection();
        tileLayer._clearBgBuffer();
    }
}
