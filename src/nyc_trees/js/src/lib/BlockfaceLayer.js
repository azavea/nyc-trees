"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapUtil = require('./mapUtil'),
    zoom = require('./mapUtil').ZOOM;

/* Adds a geojson layer to the given map, changing the stye based on the zoom
 * level */
module.exports = L.GeoJSON.extend({
    options: {
        color: undefined
    },

    initialize: function(map, options) {
        L.GeoJSON.prototype.initialize.call(this, null, options);

        if ($.type(this.options.color) !== "string") {
            throw "Must specify a 'color' option.";
        }

        var self = this;

        this.options.style = function() {
            return getStyle(map, self.options.color);
        };

        map.on('zoomend', function() {
            self.setStyle(getStyle(map, self.options.color));
        });
    }
});

function getStyle(map, color) {
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

// Note: this must be kept in sync with src/tiler/style/*.mss
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
