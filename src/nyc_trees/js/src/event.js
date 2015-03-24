"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    EventMap = require('./EventMap'),
    fetchAndReplace = require('./fetchAndReplace'),
    poller = require('./lib/poller'),

    dom = {
        map: '#map',
        rsvpSection: '#rsvp-section',
        rsvpButton: '#rsvp',
        mapLink: '[data-poll-url]'
    },

    $map = $('#map');

new EventMap({
    location: L.latLng($map.data('lat'), $map.data('lon')),
    static: true
});

fetchAndReplace({
    container: '#rsvp-section',
    target: '#rsvp'
});

require('./copyEventUrl');

var pollUrl = $(dom.mapLink).attr('data-poll-url'),
    poll = poller(pollUrl, function(data) {
        if (data && data.map_pdf_url) {
            $(dom.mapLink).html('Download');
            $(dom.mapLink).attr('href', data.map_pdf_url);
            return true;
        }
        return false;
    });

poll();
