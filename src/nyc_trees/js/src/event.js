"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    EventMap = require('./EventMap'),
    fetchAndReplace = require('./fetchAndReplace'),

    dom = {
        map: '#map',
        rsvpSection: '#rsvp-section',
        rsvpButton: '#rsvp',
        eventAlertButton: '#event-button'
    },

    $map = $('#map');

new EventMap({
    location: L.latLng($map.data('location')),
    static: true
});

fetchAndReplace({
    container: dom.rsvpSection,
    target: dom.rsvpButton,
    callback: function() {
        $(dom.eventAlertButton).toggleClass('hidden');
    }
});

require('./copyEventUrl');

require('./lib/pollForDownload');
