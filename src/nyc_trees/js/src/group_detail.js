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

$(dom.requestAccessButton).click(function() {
    var groupSlug = $(dom.requestAccessButton).data('group-slug');
    $(dom.modals).modal('hide');
    $.ajax({
            // Keep this URL in sync with "request_mapper_status"
            // in src/nyc_trees/apps/users/urls/group.py
            url: '/group/' + groupSlug + '/request-trusted-mapper-status/',
            type: 'POST'
        })
        .done(function() {
            $(dom.requestAccessCompleteModal).modal('show');
        })
        .fail(function() {
            $(dom.requestAccessFailModal).modal('show');
        });
});
