"use strict";

var L = require('leaflet'),
    zoom = require('./mapUtil').zoom,
    $ = require('jquery'),

    color = '#FFEB3B';

module.exports = {
    create: createBlockfaceLayer
};

/* Adds a geojson layer to the given map, based on the geojson data of a UtfGrid.
 * The UtfGrid must have a "geojson" property as a data attribute.
 *
 * Geojson fatures are added to the map when their corresponding
 * features are clicked in the UtfGrid, and they are removed when the geojson
 * feature is clicked.
 *
 * Accepts two callbacks: onAdd and onRemove, which are called prior to adding
 * or removing geojson features.
 *
 * If the callbacks do not return a truthy value, the feature will not be
 * added/removed.
 *
 * Returns the created geojson layer
 */
function createBlockfaceLayer(options) {
    var map = options.map,
        grid = options.grid,
        onAdd = options.onAdd || $.noop,
        onRemove = options.onRemove || $.noop,

        blockfaceLayer = L.geoJson([], {
            style: function() {
                return getStyle(map);
            },
            onEachFeature: function(feature, layer) {
                layer.on('click', function() {
                    if (onRemove(feature)) {
                        blockfaceLayer.removeLayer(layer);
                    }
                });
            }
        });

    grid.on('click', function(e) {
        if (e.data && e.data.geojson) {
            if (onAdd(e.data)) {
                blockfaceLayer.addData({
                    "type": "Feature",
                    "geometry": JSON.parse(e.data.geojson),
                    "properties": e.data
                });
            }
        }
    });

    map.addLayer(blockfaceLayer);
    map.addLayer(grid);

    map.on('zoomend', function() {
        blockfaceLayer.setStyle(getStyle(map));
    });

    return blockfaceLayer;
}

function getStyle(map) {
    return {
        color: color,
        fillColor: color,
        opacity: 1,
        lineCap: 'round',
        lineJoin: 'round',
        clickable: true,
        weight: getLineWidth(map.getZoom())
    };
}

// Note: this must be kept in sync with src/tiler/style/progress.mss
// Line widths are purposefully 1 pixel wider than the tiler styling
function getLineWidth(zoom) {
    if (zoom >= 19) {
        return 17;
    } else if (zoom === 18) {
        return 9;
    } else if (zoom === 17) {
        return 5;
    } else if (zoom === 16) {
        return 3;
    } else {
        return 2;
    }
}
