"use strict";

var MapModule = require('./map'),
    zoom = require('./mapUtil').zoom,
    L = require('leaflet');

var reservationMap = MapModule.create({
    geolocation: true,
    legend: true,
    search: true
});

// TODO: Only show this layer in "add" mode.
L.tileLayer(config.urls.layers.reservable.tiles, {
    maxZoom: zoom.MAX
}).addTo(reservationMap);
