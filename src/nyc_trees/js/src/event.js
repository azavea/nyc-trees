"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    fetchAndReplace = require('./fetchAndReplace');

var $map = $('#map');
mapModule.create({
    location: L.latLng($map.data('lat'), $map.data('lon')),
    static: true
});

fetchAndReplace({
    container: '#rsvp-section',
    target: '#rsvp'
});
