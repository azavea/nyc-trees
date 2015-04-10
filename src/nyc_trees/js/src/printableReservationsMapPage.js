"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map');

var reservationsMap = mapModule.create({
        static: true,
        forPdf: true
    }),
    endpoints = mapModule.getDomMapAttribute('endpoints'),
    endpointsLayer = new L.FeatureGroup(),
    zoom = reservationsMap.getZoom(),
    radius =
        zoom === 19 ? 24 :
        zoom === 18 ? 12 :
        zoom === 17 ?  6 : 3,
    defaultStyle = {
        opacity: 0.7,
        weight: zoom > 17 ? 2 : 1,
        color: '#4575b4',
        clickable: true,
        radius: radius
    };

$.each(endpoints, function(i, endpoint) {
    var circle = L.circleMarker(L.latLng(endpoint), defaultStyle);
    endpointsLayer.addLayer(circle);
});

reservationsMap.addLayer(endpointsLayer);

mapModule.addTileLayer(reservationsMap);