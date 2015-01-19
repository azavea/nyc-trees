"use strict";

var $ = require('jquery'),
    L = require('leaflet');

var zoomModule = require('./mapUtil').zoom,
    searchController = require('./searchController');

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

    if (options.center) {
        var zoom = options.zoom || zoomModule.NEIGHBORHOOD;
        map.setView(options.center, zoom);
    } else {
        map.fitBounds(config.bounds);
    }

    initBaseMap(map);

    if (options.geolocation && navigator.geolocation) {
        initGeolocation($controlsContainer, map);
    }
    if (options.legend) {
        initLegend($controlsContainer, map);
    }
    if (options.search) {
        initLocationSearch($controlsContainer, map);
    }

    return map;
}

function initBaseMap(map) {
    var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        osmAttrib = 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
        osm = new L.TileLayer(osmUrl, {attribution: osmAttrib});

    map.addLayer(osm);
}

function initGeolocation($controlsContainer, map) {
    var $button = $('<a class="geolocate-button" href="javascript:;" title="Show my location">X</a>');
    $controlsContainer.prepend($button);

    $button.on('click', function () {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    });

    function showPosition(position) {
        var center = L.latLng(position.coords.latitude, position.coords.longitude);
        map.setView(center, zoomModule.NEIGHBORHOOD);
    }

    function showError() {
        window.alert('Unable to show your location.');
    }

}

function initLocationSearch($controlsContainer, map) {
    searchController.create($controlsContainer, map);
}

function initLegend($controlsContainer, map) {
    var $button = $('<a class="legend-button" data-toggle="modal" href="#legend" href="javascript:;" title="Legend">L</a>');
    $controlsContainer.prepend($button);
}
