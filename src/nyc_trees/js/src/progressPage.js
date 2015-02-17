"use strict";

var mapModule = require('./map'),
    zoom = require('./mapUtil').ZOOM,
    L = require('leaflet');

var progressMap = mapModule.create({
    geolocation: true,
    legend: true,
    search: true
});

mapModule.addTileLayer(progressMap);
