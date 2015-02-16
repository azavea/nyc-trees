"use strict";

var fetchAndReplace = require('./fetchAndReplace'),
    $ = require('jquery'),
    mapModule = require('./map');

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
