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
    };
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
    if (options.crosshairs) {
        initCrosshairs(options.domId);
    }
    if (options.static) {
        // We had to add zoomControl to find its container, but now remove it.
        zoomControl.removeFrom(map);
    }

    return map;
}

function initBaseMap(map) {
    var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        osmAttrib = 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
        osm = new L.TileLayer(osmUrl, {maxZoom: zoom.MAX, attribution: osmAttrib});

    map.addLayer(osm);
}

function initGeolocation($controlsContainer, map) {
    var $button = $('<a class="geolocate-button" href="javascript:;" title="Show my location"><i class="icon-location"></i></a>');
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
    var $button = $('<a class="legend-button" data-toggle="modal" href="#legend" href="javascript:;" title="Legend">?</a>');
    $controlsContainer.prepend($button);
}

function initCrosshairs(domId) {
    var $map = $('#' + domId),
        $hHair = $('<div style="position:absolute; left:0; right:0; bottom:50%; height:1px; background:black"></div>'),
        $vHair = $('<div style="position:absolute; right:50%; width:1px; top:0; bottom:0; background:black"></div>');
    $map.append([$hHair, $vHair]);
}
