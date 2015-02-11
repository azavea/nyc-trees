"use strict";

var fetchAndReplace = require('./fetchAndReplace'),
    mapModule = require('./map');

fetchAndReplace({
    container: '.btn-follow-container',
    target: '.btn-follow, .btn-unfollow'
});

require('./event_list');
require('./copyEventUrl');

var territoryMap = mapModule.create({
    static: true
});

mapModule.addTileLayer(territoryMap);
