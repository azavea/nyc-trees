"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    fetchAndReplace = require('./fetchAndReplace');

var $map = $('#map'),
    location = L.latLng($map.data('lat'), $map.data('lon')),
    map = mapModule.create({ center: location });

L.circleMarker(location, {
    stroke: false,
    fillColor: '#198d5e',
    radius: 10,
    fillOpacity: 1
}).addTo(map);

fetchAndReplace({
    container: '#rsvp-section',
    target: '#rsvp'
});
