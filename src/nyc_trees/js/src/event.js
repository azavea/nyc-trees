"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    EventMap = require('./EventMap'),
    fetchAndReplace = require('./fetchAndReplace');

var $map = $('#map');
new EventMap({
    location: L.latLng($map.data('lat'), $map.data('lon')),
    static: true
});

fetchAndReplace({
    container: '#rsvp-section',
    target: '#rsvp'
});
