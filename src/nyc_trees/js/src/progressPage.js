"use strict";

var MapModule = require('./map'),
    L = require('leaflet');

var progressMap = MapModule.create({
    geolocation: true,
    legend: true,
    search: true
});

L.tileLayer(config.urls.layers.progress.tiles).addTo(progressMap);
