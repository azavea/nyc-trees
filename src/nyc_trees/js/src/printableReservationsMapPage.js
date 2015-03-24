"use strict";

var mapModule = require('./map');

var reservationsMap = mapModule.create({
    static: true,
    forPdf: true
});

mapModule.addTileLayer(reservationsMap);