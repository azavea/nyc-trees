"use strict";

require('./event_list');

var $ = require('jquery'),
    mapModule = require('./map'),
    mapUtil = require('./lib/mapUtil'),
    L = require('leaflet'),

    dom = {
        mapToggle: '[data-toggle="tab"][href="#map-tab"]',
        actionBar: '#action-bar',
        mainTabs: '#nav-tabs-event a',
        mapContainer: '.page-map'
    },
    geojsonPromise = $.getJSON(config.urls.geojson.events);

// We can't initialize the map until we switch to the map tab, or it will be
// sized incorrectly
$(dom.mapToggle).one('shown.bs.tab', function() {
    geojsonPromise.done(function(geojson) {
        if (geojson.length === 0) {
            mapModule.create({
                geolocation: true,
                search: true,
                // There is no raster tile layer, so labels embedded in the
                // basemap will work just fine
                withLabels: true
            });
            return;
        }

        var eventLayer = L.geoJson(geojson, {
            pointToLayer: function(feature, latLng) {
                return mapUtil.styledCircleMarker(latLng);
            }
        });

        var eventMap = mapModule.create({
            geolocation: true,
            search: true,
            bounds: eventLayer.getBounds()
        }),
        currentMarker;

        eventLayer.on('click', function(event) {
            var eventLatLng = L.GeoJSON.coordsToLatLng(
                event.layer.feature.geometry.coordinates, true);

            // Position a marker over top of the selected event
            // Prevents reloading the same event and provides a visual cue
            if (currentMarker) {
                eventMap.removeLayer(currentMarker);
            }
            currentMarker = L.circleMarker(eventLatLng, {
                stroke: false,
                fillColor: '#198d5e',
                radius: 10,
                fillOpacity: 1
            }).addTo(eventMap);

            $(dom.actionBar).load(event.layer.feature.properties.url);
        })
        .addTo(eventMap);
    });
});

$(dom.mainTabs).on('click', function (e) {
    e.preventDefault();

    var selectedTab = $(e.currentTarget).attr('href');
    $(dom.mapContainer).removeClass('tab-status-list tab-status-map-tab');

    if (selectedTab === '#map-tab') {
        $(dom.mapContainer).addClass('tab-status-map-tab');
    } else if (selectedTab === '#list') {
        $(dom.mapContainer).addClass('tab-status-list');
    }
});
