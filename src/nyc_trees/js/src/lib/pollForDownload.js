"use strict";

var $ = require('jquery'),
    poller = require('./poller'),

    $mapLink = $('[data-poll-url]');

if ($mapLink.length) {
    var pollUrl = $mapLink.attr('data-poll-url'),
        poll = poller(pollUrl, function (data) {
            if (data && data.map_pdf_url) {
                $mapLink.html('Download');
                $mapLink.attr('href', data.map_pdf_url);
                return true;
            }
            return false;
        });

    poll();
}