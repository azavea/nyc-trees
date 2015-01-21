"use strict";

/* Creates a map with a highlighted location in the center.
 * Update the location by calling setLocation().
 */

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    zoom = require('./mapUtil').zoom;

var EventMap = function (options) {
    var map = mapModule.create(options),
        marker = null;

    if (options.location && options.location.lat !== 0) {
        marker = createMarker(map, options.location);
    }

    return {
        setLocation: function (latLng) {
            if (!marker) {
                marker = createMarker(map, latLng);
            } else {
                marker.setLatLng(latLng);
            }
            map.setView(latLng, zoom.NEIGHBORHOOD);
        }
    };
};

function createMarker(map, location) {
    return L.circleMarker(location, {
        stroke: false,
        fillColor: '#198d5e',
        radius: 10,
        fillOpacity: 1,
        clickable: false
    }).addTo(map);
}

module.exports = EventMap;
