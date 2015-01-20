"use strict";

var MapModule = require('./map'),
    L = require('leaflet');

var reservationMap = MapModule.create({
    geolocation: true,
    legend: true,
    search: true
});
