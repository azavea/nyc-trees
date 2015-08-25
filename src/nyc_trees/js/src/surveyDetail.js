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
        surveyUrlAttr: 'data-survey-url',
        abandonIncomplete: '#survey-detail-abandon-incomplete',
        submitIncomplete: '#survey-detail-submit-incomplete',
        submitComplete: '#survey-detail-submit-complete',

        firstSection: '#choose-action',

        restartSection: '#restart',
        restartComment: '#restart-submit-comment',
        confirmRestart: '#survey-detail-restart-confirm',

        reviewSection: '#review',
        reviewComment: '#review-submit-comment',
        confirmReview: '#survey-detail-review-confirm',
    },

    $map = $(dom.mapSelector),
    blockfaceId = $map.attr(dom.blockfaceIdAttr),
    surveyId = $map.attr(dom.surveyIdAttr),
    treesJSON = $map.attr(dom.treesJSONAttr),
    surveyUrl = $map.attr(dom.surveyUrlAttr),
    blockfaceMap = mapModule.create({
        legend: false,
        search: false,
        baseMap: mapModule.SATELLITE
    }),

    drawLayer = new L.geoJson(null, {
        pointToLayer: function(feature, latLng) {
            return mapUtil.styledCircleMarker(latLng);
        }
    });

function postThen(postUrl, comment, callback) {
    return function () {
        var p = $.ajax({
            url: postUrl + surveyId + '/',
            data: {
                comment: $(comment).val()
            },
            type: 'POST',
            dataType: 'json'
        });

        p.done(callback);

        p.fail(function(jqXHR, textStatus, errorThrown) {
            toastr.warning('Sorry, there was a problem processing your answer. Please try again.',
                           'Something went wrong...');
        });
    };
}

blockfaceMap.addLayer(drawLayer);

mapUtil.fetchBlockface(blockfaceId).done(function(blockface) {
    blockfaceMap.fitBounds(blockface.bounds);
    drawLayer.addData(JSON.parse(blockface.geojson)).bringToBack();
    drawLayer.setStyle(mapUtil.styledStreetConfirmation);
});

$.each($(JSON.parse(treesJSON)), function (__, tree) {
    drawLayer.addData({ 'type': 'Feature', 'geometry': JSON.parse(tree) });
});

$(dom.abandonIncomplete).on('click', function() {
    $(dom.firstSection).addClass('hidden');
    $(dom.restartSection).removeClass('hidden');
});

$(dom.submitIncomplete).on('click', function() {
    $(dom.firstSection).addClass('hidden');
    $(dom.reviewSection).removeClass('hidden');
});

$(dom.reviewComment).on('blur change keyup paste', function() {
    var text = $(dom.reviewComment).val();
    $(dom.confirmReview).prop('disabled', text.trim() === '');
});

$(dom.confirmRestart).on('click', postThen('/survey/restart_blockedge/', dom.restartComment, function () {
    // Note: this URL needs to be kept in sync with
    // src/nyc_trees/apps/survey/urls/survey.py
    window.location.href = surveyUrl + '#' + blockfaceId;
}));

$(dom.confirmReview).on('click', postThen('/survey/flag/', dom.reviewComment, mapAnotherPopup.show));

$(dom.submitComplete).on('click', mapAnotherPopup.show);
