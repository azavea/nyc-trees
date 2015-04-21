"use strict";

var $ = require('jquery'),
    fetchAndReplace = require('./fetchAndReplace'),
    mapModule = require('./map');

var dom = {
    modals: '.modal',
    requestAccessButton: '[data-action="request-access"]',
    requestAccessCompleteModal: '#request-access-complete-modal',
    requestAccessFailModal: '#request-access-fail-modal'
};

fetchAndReplace({
    container: '.follow-detail',
    target: '.btn-follow, .btn-unfollow'
});

require('./event_list');
require('./copyEventUrl');

if ($('#map').length > 0) {
    var territoryMap = mapModule.create({
        static: true
    });

    mapModule.addTileLayer(territoryMap);
}
