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
        addBlockface(e.data);
    });

    function addBlockface(data) {
        if (data && data.geojson) {
            if (onAdd(data)) {
                blockfaceLayer.addData({
                    "type": "Feature",
                    "geometry": JSON.parse(data.geojson),
                    "properties": data
                });
            }
        }
    }

    map.addLayer(blockfaceLayer);
    map.addLayer(grid);

    map.on('zoomend', function() {
        blockfaceLayer.setStyle(getStyle(map));
    });

    return {
        addBlockface: addBlockface
    };
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
// Line widths are purposefully 2 pixels wider than the tiler styling
function getLineWidth(zoom) {
    if (zoom >= 19) {
        return 18;
    } else if (zoom === 18) {
        return 10;
    } else if (zoom === 17) {
        return 6;
    } else if (zoom === 16) {
        return 4;
    } else {
        return 3;
    }
}
