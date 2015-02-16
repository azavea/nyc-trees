"use strict";

var fetchAndReplace = require('./fetchAndReplace'),
    mapModule = require('./map');

fetchAndReplace({
    container: '.follow-detail',
    target: '.btn-follow, .btn-unfollow'
});

require('./event_list');
require('./copyEventUrl');

var territoryMap = mapModule.create({
    static: true
});

mapModule.addTileLayer(territoryMap);
