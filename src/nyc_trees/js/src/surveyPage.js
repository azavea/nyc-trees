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

            $(dom.selectStartingPoint).removeClass('hidden');
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

// Temporary code to test submitting survey data.
// Assumes user has reserved the blockface (not mapping at event)
$(dom.btnNext).click(function(e) {
    var data = {
        survey: {
            blockface_id: blockfaceId,
            is_flagged: false,
            has_trees: true,
            is_mapped_in_blockface_polyline_direction: true,
            is_left_side: true
        },
        trees: [
            {
                circumference: 10,
                distance_to_tree: 100,
                curb_location: 'OnCurb',
                status: 'Alive',
                species_certainty: 'Yes',
                health: 'Good',
                stewardship: 'None',
                guards: 'None',
                sidewalk_damage: 'NoDamage',
                problems: ['Stones', 'Sneakers']
            }
        ]
    };
    $.ajax('/survey/', {
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(data)
        })
        .done(function(content) {
            window.alert('Successfully saved a test survey');
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            window.alert(errorThrown);
        });
});
