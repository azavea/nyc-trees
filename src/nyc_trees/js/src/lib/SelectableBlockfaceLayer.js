"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    zoom = require('../mapUtil').zoom,

    color = '#FFEB3B';

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
 */
module.exports = L.GeoJSON.extend({
    options: {
        onAdd: $.noop,
        onRemove: $.noop
    },

    initialize: function(map, grid, options) {
        L.GeoJSON.prototype.initialize.call(this, null, options);

        var self = this;

        this.options.style = function() {
            return getStyle(map);
        };

        this.options.onEachFeature = function(feature, layer) {
            layer.on('click', function() {
                if (self.options.onRemove(feature)) {
                    self.removeLayer(layer);
                }
            });
        };

        grid.on('click', function(e) {
            self.addBlockface(e.data);
        });

        map.on('zoomend', function() {
            self.setStyle(getStyle(map));
        });
    },

    addBlockface: function(data) {
        if (data && data.geojson) {
            if (this.options.onAdd(data)) {
                this.addData({
                    "type": "Feature",
                    "geometry": JSON.parse(data.geojson),
                    "properties": data
                });
            }
        }
    }
});

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
