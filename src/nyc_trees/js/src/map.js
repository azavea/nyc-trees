
"use strict";

var $ = require('jquery'),
    L = require('leaflet');

var zoom = require('./lib/mapUtil').ZOOM,
    SATELLITE = 'satellite',
    searchController = require('./searchController'),
    labelLayer = null;


module.exports = {
    SATELLITE: SATELLITE,
    create: create,
    createAndGetControls: createAndGetControls,
    addTileLayer: addTileLayer,
    addGridLayer: addGridLayer,
    fitBounds: fitBounds,
    getDomMapAttribute: getDomMapAttribute,
    hideCrosshairs: hideCrosshairs,
    startTrackingUserPosition: startTrackingUserPosition,
    stopTrackingUserPosition: stopTrackingUserPosition
};

function create(options) {
    return createAndGetControls(options).map;
}

function createAndGetControls(options) {
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
        // We have stretched the zoomControl and its "container" (which is
        // not its parent as once thought but rather its DOM element)
        // into a multi-purpose widget control. This is done by
        // instantiating a zoom control and then placing additional markup
        // in its DOM element for other controls. Subsequently, we
        // refer to it as the multiControl in order to hide this
        // implementation detail.
        multiControl = L.control.zoom({position: 'bottomleft'}).addTo(map),
        $multiControlContainer = $(multiControl.getContainer()),
        bounds = getDomMapAttribute('bounds', options.domId),
        mapLocation = getDomMapAttribute('location', options.domId),
        zoomSpec = getDomMapAttribute('zoom', options.domId);

    map.addControl(L.control.attribution({prefix: false}));

    if (bounds) {
        fitBounds(map, bounds);
    } else if (options.bounds) {
        map.fitBounds(options.bounds, {maxZoom: zoom.NEIGHBORHOOD});
    } else if (mapLocation) {
        var z = (zoomSpec === 'LOCATION' ? zoom.LOCATION : zoom.NEIGHBORHOOD);
        map.setView(mapLocation, z);
    } else if (options.location && options.location.lat !== 0) {
        map.setView(options.location, zoom.NEIGHBORHOOD);
    } else {
        map.fitBounds(config.bounds);
    }

    initBaseMap(map, options);

    if (options.geolocation && navigator.geolocation) {
        initGeolocation($multiControlContainer, map);
    }
    if (options.legend) {
        initLegend($multiControlContainer, map);
    }
    if (options.search) {
        initLocationSearch($multiControlContainer, map);
    }
    if (options.crosshairs) {
        initCrosshairs(options.domId);
    }
    if (options.static) {
        // We had to add zoomControl to find its container, but now remove it.
        multiControl.removeFrom(map);
    }

    return {map: map, multiControl: multiControl};
}

// Return a promise which is resolved when map is done zooming.
function fitBounds(map, bounds) {
    if (!bounds) {
        return $.Deferred().resolve().promise();
    }

    // GeoDjango bounds are [xmin, ymin, xmax, ymax]
    // Leaflet wants [ [ymin, xmin], [ymax, xmax] ]
    var b = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]],
        zooming = (map.getZoom() !== map.getBoundsZoom(b)),
        defer = $.Deferred();

    if (zooming) {
        map.on('zoomend', defer.resolve);
    } else {
        defer.resolve();
    }

    map.fitBounds(b);
    return defer.promise();
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
        labelLayerOptions =  {
            subdomains: 'abcd',
            minZoom: zoom.MIN,
            maxZoom: zoom.MAX,
            opacity: 0.75,
            attribution: 'Map labels by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>'
        },
        satelliteUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        withoutLabelsUrl = 'cartodb-basemaps-{s}.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}',
        withLabelsUrl = 'cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}',
        labelsOnlyUrl = 'stamen-tiles-{s}.a.ssl.fastly.net/toner-labels/{z}/{x}/{y}',

        protocol = options.forPdf ? 'http://' : 'https://',  // PhantomJS fails with https
        standardUrl = options.withLabels ? withLabelsUrl : withoutLabelsUrl,
        suffix = (options.forPdf || isRetinaDevice()) ? '@2x.png' : '.png',

        url = options.baseMap === SATELLITE ? satelliteUrl : protocol + standardUrl + suffix;

    map.addLayer(new L.TileLayer(url, layerOptions));

    if (options.baseMap !== SATELLITE && !options.withLabels) {
        labelLayer = new L.TileLayer(protocol + labelsOnlyUrl + suffix, layerOptions);
        labelLayer.setOpacity(0.75);
        map.addLayer(labelLayer);
    }
}

function initGeolocation($controlsContainer, map) {
    var $button = $('<a class="geolocate-button" href="javascript:;" title="Show my location"><i class="icon-target"></i></a>');
    $controlsContainer.prepend($button);

    $button.on('click', function () {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    });

    function showPosition(position) {
        var center = L.latLng(position.coords.latitude, position.coords.longitude);
        map.setView(center, zoom.LOCATION);
    }

    function showError() {
        window.alert('Unable to show your location.');
    }
}

function initLocationSearch($multiControlContainer, map) {
    searchController.create($multiControlContainer, map);
}

function initLegend($multiControlContainer, map) {
    var $button = $(
        '<a class="legend-button" data-toggle="modal" href="#legend" href="javascript:;" title="Legend">?</a>');
    $multiControlContainer.prepend($button);
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
            minZoom: options.minZoom || zoom.MIN,
            maxZoom: options.maxZoom || zoom.MAX
        });
    map.addLayer(layer);
    if (labelLayer) {
        labelLayer.bringToFront();
    }
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
    map.addLayer(layer);
    return layer;
}

function getDomMapAttribute(dataAttName, domId) {
    domId = domId || 'map';
    var $map = $('#' + domId),
        value = $map.data(dataAttName);
    return value;
}

function startTrackingUserPosition(map) {
    map.on('locationfound', onLocationFound);
    map.on('locationerror', onLocationError);
    map.on('unload', stopTrackingUserPosition);
    map.locate({watch: true, enableHighAccuracy: true});
}

function stopTrackingUserPosition(map) {
    var marker = map._userLocationMarker;
    if (marker) {
        map.removeLayer(marker);
    }
    map.off('locationfound', onLocationFound);
    map.off('locationerror', onLocationError);
    map.off('unload', stopTrackingUserPosition);
    map.stopLocate();
}

function onLocationFound(e) {
    var map = e.target,
        marker = map._userLocationMarker,
        latlng = e.latlng;

    // For testing, move points near Azavea to southern Manhattan
    var azaveaLatLng = L.latLng(39.9583208, -75.1585257),
        manhattanLatLng = L.latLng(40.7030809, -74.0129269);
    if (latlng.distanceTo(azaveaLatLng) < 1000) {
        latlng.lat += manhattanLatLng.lat - azaveaLatLng.lat;
        latlng.lng += manhattanLatLng.lng - azaveaLatLng.lng;
    }

    if (!marker) {
        marker = map._userLocationMarker = L.circleMarker(latlng, {
            color: '#0E9C4B',
            fillColor: '#00EB66',
            fillOpacity: 1.0,
            weight: 2,
            opacity: 1.0,
            radius: 8
        });
    }
    if (!map.hasLayer(marker)) {
        map.addLayer(marker);
    }
    marker.setLatLng(latlng);
}

function onLocationError(e) {
    var map = e.target;
    if (e.code == 3) {
        return;  // ignore timeouts
    }
    stopTrackingUserPosition(map);
}
