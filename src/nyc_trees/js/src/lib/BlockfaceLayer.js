"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapUtil = require('./mapUtil'),
    zoom = require('./mapUtil').ZOOM;

/* Adds a geojson layer to the given map, changing the stye based on the zoom
 * level */
module.exports = L.GeoJSON.extend({
    options: {
        color: undefined,
        dashArray: undefined,
        thin: false
    },

    initialize: function(map, options) {
        L.GeoJSON.prototype.initialize.call(this, null, options);

        if ($.type(this.options.color) !== "string") {
            throw "Must specify a 'color' option.";
        }

        var self = this;

        this.options.style = function() {
            return getStyle(map, self.options);
        };

        map.on('zoomend', function() {
            self.setStyle(getStyle(map, self.options));
        });
    }
});

function getStyle(map, options) {
    return {
        color: options.color,
        fillColor: options.color,
        dashArray: options.dashArray,
        lineCap: 'round',
        lineJoin: 'round',
        clickable: true,
        opacity: 1,
        weight: getLineWidth(map.getZoom(), options.thin)
    };
}

// Note: this must be kept in sync with src/tiler/style/*.mss
// Line widths are purposefully 2 pixels wider than the tiler styling
// The "Mapped" lines on the progress map never get smaller than 6 pixels,
// so we never make our selected line smaller than 8 pixels
// (even for unmapped / non progress page lines), unless the "thin" option
// is provided when creating this layer.
function getLineWidth(zoom, thin) {
    if (zoom >= 19) {
        return 18;
    } else if (zoom === 18) {
        return 10;
    } else if (thin) {
        if (zoom === 17) {
            return 6;
        } else if (zoom === 16) {
            return 4;
        } else if (zoom <= 15) {
            return 3;
        }
    } else {
        // The selected lines on the progress page are always 6px or greater
        return 8;
    }
}
