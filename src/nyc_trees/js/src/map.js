"use strict";

var $ = require('jquery'),
    L = require('leaflet');

module.exports = {
    create: create
};

function create(options) {
    options = $.extend({
        domId: 'map'
    }, options);

    var map = L.map(options.domId),
        osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        osmAttrib = 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
        osm = new L.TileLayer(osmUrl, {attribution: osmAttrib});

    map.addLayer(osm);

    // New York City bounds from http://www.mapdevelopers.com/geocode_bounding_box.php
    map.fitBounds([
        [40.495996, -74.259088],
        [40.915256, -73.700272]
    ]);

    return map;
}
