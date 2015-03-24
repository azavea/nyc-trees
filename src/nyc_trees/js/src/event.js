"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    EventMap = require('./EventMap'),
    fetchAndReplace = require('./fetchAndReplace'),

    dom = {
        map: '#map',
        rsvpSection: '#rsvp-section',
        rsvpButton: '#rsvp'
    },

    $map = $('#map');

new EventMap({
    location: L.latLng($map.data('lat'), $map.data('lon')),
    static: true
});

fetchAndReplace({
    container: dom.rsvpSection,
    target: dom.rsvpButton
});

require('./copyEventUrl');

require('./lib/pollForDownload');
