"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    mapUtil = require('./lib/mapUtil'),
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer');

// Extends the leaflet object
require('leaflet-utfgrid');

var dom = {
    selectStartingPoint: '#select-starting-point',
    selectSide: '#select-side',
    leftRightButtons: '#btn-left, #btn-right',
    btnGroupNext: '#btn-group-next',
    btnNext: '#btn-next'
};

var blockfaceId = mapUtil.getBlockfaceIdFromUrl(),
    blockfaceMap = mapModule.create({
        legend: true,
        search: true
    });

var endPointLayers = new L.FeatureGroup(),
    defaultStyle = {
        opacity: 0.7,
        weight: 2,
        color: '#4575b4',
        clickable: true,
        radius: 25
    },
    selectStyle = {
        opacity: 0.9,
        weight: 3,
        color: '#ff0000',
        clickable: false
    };

var tileLayer = mapModule.addTileLayer(blockfaceMap),
    grid = mapModule.addGridLayer(blockfaceMap),

    selectedLayer = new SelectableBlockfaceLayer(blockfaceMap, grid, {
        onAdd: function(gridData, geom) {
            var latLngs = mapUtil.getLatLngs(geom);

            blockfaceId = gridData.id;

            selectedLayer.clearLayers();
            endPointLayers.clearLayers();

            endPointLayers.addLayer(
                L.circleMarker(latLngs[0], defaultStyle)
            );
            endPointLayers.addLayer(
                L.circleMarker(latLngs[latLngs.length - 1], defaultStyle)
            );

            $(dom.selectSide).addClass('hidden');
            $(dom.btnGroupNext).addClass('hidden');

            mapUtil.zoomToBlockface(blockfaceMap, blockfaceId);
            return true;
        }
    });

blockfaceMap.addLayer(selectedLayer);
blockfaceMap.addLayer(endPointLayers);

endPointLayers.setStyle(defaultStyle);
endPointLayers.on('click', function(e) {
    endPointLayers.setStyle(defaultStyle);
    e.layer.setStyle(selectStyle);

    $(dom.selectStartingPoint).addClass('hidden');
    $(dom.leftRightButtons).removeClass('active');
    $(dom.selectSide).removeClass('hidden');
    $(dom.btnGroupNext).addClass('hidden');
});

$(dom.leftRightButtons).click(function(e) {
    $(dom.leftRightButtons).removeClass('active');
    $(this).addClass('active');
    $(dom.btnGroupNext).removeClass('hidden');
});

mapUtil.fetchBlockface(blockfaceId).done(function(blockface) {
    selectedLayer.addBlockface(blockface);
});

function showPage(selector) {
    var pages = $(dom.pageContainer).children();
    pages.addClass('hidden');
    pages.filter(selector).removeClass('hidden');
}

$(dom.btnNext).click(function(e) {
    showPage(dom.surveyPage);
});
