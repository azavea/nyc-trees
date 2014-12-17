"use strict";

var $ = require('jquery'),
    dom = {
        eventListContainer: '[data-class="event-list-container"]',
        eventListActionLink: '[data-class="event-list-action"]'
    };

$(dom.eventListContainer).on('click', dom.eventListActionLink, function (e) {
    var $anchor = $(e.currentTarget),
        $container = $anchor.closest(dom.eventListContainer),
        url = $anchor.attr('data-url');
    e.preventDefault();
    $container.load(url);
});

