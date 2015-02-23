"use strict";

var $ = require('jquery'),
    L = require('leaflet');

var _ZOOM = {
    NEIGHBORHOOD: 16,
    MIN: 8,
    MAX: 19
};

module.exports = {
    ZOOM: Object.freeze ? Object.freeze(_ZOOM) : _ZOOM,

    setCenterAndZoomLL: function(map, zoom, mapLocation) {
        // Never zoom out, or try to zoom farther than allowed.
        var zoomToApply = Math.max(
            map.getZoom(),
            Math.min(zoom, map.getMaxZoom()));

        map.setView(mapLocation, zoomToApply);
    },

    getBlockfaceIdFromUrl: function() {
        // Assumes that the hash contains only a blockface ID
        return window.location.hash.substring(1);
    },

    getBlockfaceBounds: function(blockfaceId) {
        var defer = $.Deferred();
        if (!blockfaceId) {
            defer.reject();
        } else {
            // NOTE: This has a hard coded url that must be kept in sync with
            // apps/survey/urls/blockface.py
            $.getJSON('/blockface/' + blockfaceId + '/', function(blockface) {
                var e = blockface.extent,
                    sw = L.latLng(e[1], e[0]),
                    ne = L.latLng(e[3], e[2]),
                    bounds = L.latLngBounds(sw, ne);
                defer.resolve(bounds);
            });
        }
        return defer.promise();
    }
};
