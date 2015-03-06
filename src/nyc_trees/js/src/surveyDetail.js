"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    toastr = require('toastr'),
    mapModule = require('./map'),
    mapUtil = require('./lib/mapUtil'),
    mapAnotherPopup = require('./mapAnotherPopup'),

    dom = {
        mapSelector: '#map',
        surveyIdAttr: 'data-survey-id',
        blockfaceIdAttr: 'data-blockface-id',
        treesJSONAttr: 'data-trees-json',
        abandonIncomplete: '#survey-detail-abandon-incomplete',
        submitIncomplete: '#survey-detail-submit-incomplete',
        submitComplete: '#survey-detail-submit-complete'
    },

    blockfaceId = $(dom.mapSelector).attr(dom.blockfaceIdAttr),
    surveyId = $(dom.mapSelector).attr(dom.surveyIdAttr),
    treesJSON = $(dom.mapSelector).attr(dom.treesJSONAttr),
    blockfaceMap = mapModule.create({
        legend: false,
        search: false
    }),

    drawLayer = new L.geoJson(null, {
        pointToLayer: function(feature, latLng) {
            return mapUtil.styledCircleMarker(latLng);
        }
    });

function postAndPrompt(postUrl) {
    return function () {
        var p = $.ajax({
            url: postUrl + surveyId + '/',
            type: 'POST',
            dataType: 'json'
        });

        p.done(mapAnotherPopup.show);

        p.fail(function(jqXHR, textStatus, errorThrown) {
            toastr.warning('Sorry, there was a problem saving the survey. Please try again.',
                           'Something went wrong...');
        });
    };
}

blockfaceMap.addLayer(drawLayer);

mapUtil.fetchBlockface(blockfaceId).done(function(blockface) {
    blockfaceMap.fitBounds(blockface.bounds);
    drawLayer.addData(JSON.parse(blockface.geojson));
});

$.each($(JSON.parse(treesJSON)), function (__, tree) {
    drawLayer.addData({ 'type': 'Feature', 'geometry': JSON.parse(tree) });
});

$(dom.abandonIncomplete).on('click', function () { window.location.href = '/survey/#' + blockfaceId; });

$(dom.submitIncomplete).on('click', postAndPrompt('/survey/flag/'));

$(dom.submitComplete).on('click', postAndPrompt('/survey/complete/'));
