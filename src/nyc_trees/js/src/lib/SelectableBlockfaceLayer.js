"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    BlockfaceLayer = require('./BlockfaceLayer'),
    mapUtil = require('./mapUtil'),
    zoom = require('./mapUtil').ZOOM,

    color = '#FFEB3B';

/* Adds a geojson layer to the given map, based on the geojson data of a UtfGrid.
 * The UtfGrid must have a "geojson" property as a data attribute.
 *
 * Geojson fatures are added to the map when their corresponding
 * features are clicked in the UtfGrid, and they are removed when the geojson
 * feature is clicked.
 *
 * Accepts two callbacks: onAdd and onRemove, which are called prior to adding
 * or removing geojson features.
 *
 * If the callbacks do not return a truthy value, the feature will not be
 * added/removed.
 *
 */
module.exports = BlockfaceLayer.extend({
    options: {
        onAdd: $.noop,
        onRemove: $.noop,
        onAdded: $.noop,
        color: color
    },

    clicksEnabled: true,

    initialize: function(map, grid, options) {
        BlockfaceLayer.prototype.initialize.call(this, map, options);

        var self = this;

        this.options.onEachFeature = function(feature, layer) {
            self.options.onAdded(feature, layer);
            layer.on('click', function() {
                if (self.clicksEnabled && self.options.onRemove(feature)) {
                    self.removeLayer(layer);
                }
            });
        };

        grid.on('click', function(e) {
            if (self.clicksEnabled) {
                self.addBlockface(e.data);
            }
        });
    },

    addBlockface: function(data) {
        if (data && data.geojson) {
            var geom = mapUtil.parseGeoJSON(data.geojson);
            if (this.options.onAdd(data, geom)) {
                this.addData({
                    "type": "Feature",
                    "geometry": geom,
                    "properties": data
                });
            }
        }
    }
});
