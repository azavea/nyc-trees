"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    mapUtil = require('./lib/mapUtil'),

    dom = {
        mapSelector: '#map',
        blockfaceIdAttr: 'data-blockface-id',
        treesJSONAttr: 'data-trees-json'
    },

    blockfaceId = $(dom.mapSelector).attr(dom.blockfaceIdAttr),
    treesJSON = $(dom.mapSelector).attr(dom.treesJSONAttr),
    blockfaceMap = mapModule.create({
        legend: false,
        search: false
    }),

    drawLayer = new L.geoJson(null, {
        pointToLayer: function(feature, latLng) {
            return mapUtil.styledCircleMarker(latLng);
        }
    });

blockfaceMap.addLayer(drawLayer);

mapUtil.fetchBlockface(blockfaceId).done(function(blockface) {
    blockfaceMap.fitBounds(blockface.bounds);
    drawLayer.addData(JSON.parse(blockface.geojson));
});

$.each($(JSON.parse(treesJSON)), function (__, tree) {
    drawLayer.addData({ 'type': 'Feature', 'geometry': JSON.parse(tree) });
});
