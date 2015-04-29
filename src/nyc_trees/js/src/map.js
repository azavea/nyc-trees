
"use strict";

var $ = require('jquery'),
    L = require('leaflet');

var zoom = require('./lib/mapUtil').ZOOM,
    SATELLITE = 'satellite',
    searchController = require('./searchController');

module.exports = {
    SATELLITE: SATELLITE,
    create: create,
    addTileLayer: addTileLayer,
    addGridLayer: addGridLayer,
    fitBounds: fitBounds,
    getDomMapAttribute: getDomMapAttribute,
    hideCrosshairs: hideCrosshairs
};

function create(options) {
    options = $.extend({
        domId: 'map'
    }, options);

    var mapOptions = {
        minZoom: zoom.MIN,
        maxZoom: zoom.MAX,
        attributionControl: false,
        zoomControl: false,
        maxBounds: L.latLngBounds(config.bounds[0], config.bounds[1]).pad(4)
    };
    if (options.static) {
        mapOptions.dragging = false;
        mapOptions.touchZoom = false;
        mapOptions.scrollWheelZoom = false;
        mapOptions.doubleClickZoom = false;
        mapOptions.boxZoom = false;
        mapOptions.tap = false;
    }

    var map = L.map(options.domId, mapOptions),
        zoomControl = L.control.zoom({position: 'bottomleft'}).addTo(map),
        $controlsContainer = $(zoomControl.getContainer()),
        bounds = getDomMapAttribute('bounds', options.domId);

    map.addControl(L.control.attribution({prefix: false}));

    if (bounds) {
        fitBounds(map, bounds);
    } else if (options.bounds) {
        map.fitBounds(options.bounds, {maxZoom: zoom.NEIGHBORHOOD});
    } else if (options.location && options.location.lat !== 0) {
        map.setView(options.location, zoom.NEIGHBORHOOD);
    } else {
        map.fitBounds(config.bounds);
    }

    initBaseMap(map, options);

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
    var b = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]],
        zooming = (map.getZoom() !== map.getBoundsZoom(b));
    map.fitBounds(b);
    return zooming;
}

function isRetinaDevice() {
    return window.devicePixelRatio && window.devicePixelRatio > 1;
}

function initBaseMap(map, options) {
    var attribution = '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
                'contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
        attributionForPdf = '&copy; OpenStreetMap contributors, &copy; CartoDB',
        layerOptions =  {
            subdomains: 'abcd',
            minZoom: zoom.MIN,
            maxZoom: zoom.MAX,
            attribution: options.forPdf ? attributionForPdf : attribution
        },
        satelliteUrl = 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        strandardResUrl = 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
        retinaSuffix = 'cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}@2x.png',
        retinaUrl = 'https://' + retinaSuffix,
        retinaUrlForPdf = 'http://' + retinaSuffix,  // PhantomJS fails with https
        url =
            options.baseMap === SATELLITE ? satelliteUrl :
            options.forPdf ? retinaUrlForPdf :
            isRetinaDevice() ? retinaUrl : strandardResUrl;
    map.addLayer(new L.TileLayer(url, layerOptions));
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
    var $button = $(
        '<a class="legend-button" data-toggle="modal" href="#legend" href="javascript:;" title="Legend">?</a>');
    $controlsContainer.prepend($button);
}

function initCrosshairs(domId) {
    var $map = $('#' + domId),
        $hHair = $('<div class="crosshair-x"></div>'),
        $vHair = $('<div class="crosshair-y"></div>');
    $map.append([$hHair, $vHair]);
}

function hideCrosshairs() {
    $('.crosshair-x, .crosshair-y').hide();
}

function addTileLayer(map, options) {
    options = options || {};
    var tileUrl = options.url || getDomMapAttribute('tile-url'),
        layer = L.tileLayer(tileUrl, {
            minZoom: zoom.MIN,
            maxZoom: zoom.MAX
        });
    _addLayer(map, layer, options.waitForZoom);
    return layer;
}

function addGridLayer(map, options) {
    options = options || {};
    var gridUrl = options.url || getDomMapAttribute('grid-url'),
        layer = L.utfGrid(gridUrl, {
            minZoom: zoom.MIN,
            maxZoom: zoom.MAX,
            useJsonP: false,
            crosshairs: options.crosshairs || false,
            pointerCursor: !options.crosshairs
        });
    _addLayer(map, layer, options.waitForZoom);
    return layer;
}

function _addLayer(map, layer, waitForZoom) {
    if (waitForZoom) {
        _addAfterZoom(map, layer);
    } else {
        map.addLayer(layer);
    }
}

function _addAfterZoom(map, layer) {
    // Add layer to map after zoom animation completes.
    // (Otherwise spurious tile requests will be issued at the old zoom level.)
    function addLayer() {
        map.addLayer(layer);
        map.off('zoomend', addLayer);
    }
    map.on('zoomend', addLayer);
}

function getDomMapAttribute(dataAttName, domId) {
    domId = domId || 'map';
    var $map = $('#' + domId),
        value = $map.data(dataAttName);
    return value;
}
