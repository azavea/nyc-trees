"use strict";

var MapModule = require('./map'),
    zoom = require('./mapUtil').zoom,
    L = require('leaflet');

var progressMap = MapModule.create({
    geolocation: true,
    legend: true,
    search: true
});

L.tileLayer(config.urls.layers.progress.tiles, {
    maxZoom: zoom.MAX
}).addTo(progressMap);
