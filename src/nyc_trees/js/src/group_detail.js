"use strict";

var $ = require('jquery'),
    dom = {
        eventInfoSubmenu: '[data-class="group-detail-event-info-submenu"]',
        eventInfoSubmenuToggle: '[data-class="group-detail-event-info-submenu-toggle"]'
    };

// Needed for Follow button event handlers.
require('./followGroupButton');

$(dom.eventInfoSubmenuToggle).on('click', function (e) {
    e.preventDefault();
    $(e.target).siblings(dom.eventInfoSubmenu).toggle();
});
