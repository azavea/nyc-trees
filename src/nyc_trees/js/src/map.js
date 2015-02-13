
"use strict";

var $ = require('jquery'),
    L = require('leaflet');

var zoom = require('./mapUtil').zoom,
    searchController = require('./searchController');

module.exports = {
    create: create,
    addTileLayer: addTileLayer,
    addGridLayer: addGridLayer
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
        $controlsContainer = $(zoomControl.getContainer()),
        bounds = getDomMapAttribute('bounds');

    if (bounds) {
        fitBounds(map, bounds);
    } else if (options.location && options.location.lat !== 0) {
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

function fitBounds(map, bounds) {
    // GeoDjango bounds are [xmin, ymin, xmax, ymax]
    // Leaflet wants [ [ymin, xmin], [ymax, xmax] ]
    var b = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]];
    map.fitBounds(b);
}

function initBaseMap(map) {
    var url = 'http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png',
        options = {
            subdomains: 'abcd',
            attributon: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, ' +
                '<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; ' +
                'Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            minZoom: 0,
            maxZoom: zoom.MAX
        };

    map.addLayer(new L.TileLayer(url, options));
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

function addTileLayer(map, domId) {
    var tileUrl = getDomMapAttribute('tile-url', domId),
        layer = L.tileLayer(tileUrl, {
            maxZoom: zoom.MAX
        }).addTo(map);
    return layer;
}

function addGridLayer(map, domId) {
    var gridUrl = getDomMapAttribute('grid-url', domId),
        layer = L.utfGrid(gridUrl, {
            maxZoom: zoom.MAX,
            useJsonP: false
        });
    map.addLayer(layer);
    return layer;
}

function getDomMapAttribute(dataAttName, domId) {
    domId = domId || 'map';
    var $map = $('#' + domId),
        value = $map.data(dataAttName);
    return value;
}
