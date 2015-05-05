"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    EventMap = require('./EventMap');

var $map = $('#map'),
    eventMap = new EventMap({
        location: L.latLng($map.data('location')),
        static: true,
        forPdf: true
    });
mapModule.addTileLayer(eventMap.map);
