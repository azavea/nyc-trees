"use strict";

var $ = require('jquery'),
    L = require('leaflet');

var zoom = require('./mapUtil').zoom,
    searchController = require('./searchController');

module.exports = {
    create: create
};

function create(options) {
    options = $.extend({
        domId: 'map'
    }, options);

    var mapOptions = {
        zoomControl: false
    }
    if (options.static) {
        mapOptions.dragging = false;
        mapOptions.touchZoom = false;
        mapOptions.scrollWheelZoom = false;
        mapOptions.doubleClickZoom = false;
        mapOptions.boxZoom = false;
    }

    var map = L.map(options.domId, mapOptions),
        zoomControl = L.control.zoom({position: 'bottomleft'}).addTo(map),
        $controlsContainer = $(zoomControl.getContainer());

    if (options.location && options.location.lat !== 0) {
        map.setView(options.location, zoom.NEIGHBORHOOD);
        addLocationMarker(map, options.location);
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
    if (options.static) {
        // We had to add zoomControl to find its container, but now remove it.
        zoomControl.removeFrom(map);
    }

    return map;
}

function addLocationMarker(map, location) {
    L.circleMarker(location, {
        stroke: false,
        fillColor: '#198d5e',
        radius: 10,
        fillOpacity: 1
    }).addTo(map);
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
        map.setView(center, zoom.NEIGHBORHOOD);
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
