"use strict";

var MapModule = require('./map'),
    L = require('leaflet');

var reservationMap = MapModule.create({
    geolocation: true,
    legend: true,
    search: true
});

// TODO: Only show this layer in "add" mode.
L.tileLayer(config.urls.layers.reservable.tiles).addTo(reservationMap);
