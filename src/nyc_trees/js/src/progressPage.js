"use strict";

var $ = require('jquery'),
    zoom = require('./lib/mapUtil').ZOOM,
    L = require('leaflet'),
    mapModule = require('./map'),
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer');

// Extends the leaflet object
require('leaflet-utfgrid');

var progressMap = mapModule.create({
        geolocation: true,
        legend: true,
        search: true
    }),

    dom = {
        actionBar: '#action-bar'
    },
    $actionBar = $(dom.actionBar);

mapModule.addTileLayer(progressMap);

var grid = mapModule.addGridLayer(progressMap),

    selectedLayer = new SelectableBlockfaceLayer(progressMap, grid, {
        onAdd: function(gridData) {
            selectedLayer.clearLayers();

            // Note: this must be kept in sync with
            // src/nyc_trees/apps/survey/urls/blockface.py
            var url =
                    '/blockface/' + gridData.id +
                    '/progress-page-blockface-popup?survey_type=' + gridData.survey_type;
            if (gridData.group_id) {
                url += '&group_id=' + gridData.group_id;
            }
            $actionBar.load(url);
            return true;
        }
    });

progressMap.addLayer(selectedLayer);
