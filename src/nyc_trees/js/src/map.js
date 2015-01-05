"use strict";

var $ = require('jquery'),
    L = require('leaflet');

var zoom = {
    NEIGHBORHOOD: 16
};

module.exports = {
    create: create
};

function create(options) {
    options = $.extend({
        domId: 'map'
    }, options);

    var map = L.map(options.domId, {
            zoomControl: false
        }),
        zoomControl = L.control.zoom({position: 'bottomleft'}).addTo(map),
        $controlsContainer = $(zoomControl.getContainer());

    initBaseMap(map);

    if (options.geolocation && navigator.geolocation) {
        initGeolocation($controlsContainer, map);
    }

    // New York City bounds from http://www.mapdevelopers.com/geocode_bounding_box.php
    map.fitBounds([
        [40.495996, -74.259088],
        [40.915256, -73.700272]
    ]);

    return map;
}

function initBaseMap(map) {
    var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        osmAttrib = 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
        osm = new L.TileLayer(osmUrl, {attribution: osmAttrib});

    map.addLayer(osm);
}

function initGeolocation($controlsContainer, map) {
    var $button = $('<a class="geolocate-button" href="javascript:;" title="Show my location">X</a>')
    $controlsContainer.prepend($button);

    $button.on('click', function () {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    });

    function showPosition(position) {
        var center = L.latLng(position.coords.latitude, position.coords.longitude);
        map.setView(center, zoom.NEIGHBORHOOD);
    }

    function showError() {
        alert('Unable to show your location.');
    }

}