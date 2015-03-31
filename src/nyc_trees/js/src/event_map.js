"use strict";

require('bootstrap');

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    EventMap = require('./EventMap'),
    locationSearch = require('./searchController').locationSearch;

var dom = {
    addressStates: '#address-search .state',
    addressField: '#id_address',
    addressSearchButton: '#address-search .location-search-box',
    editButton: '.js-edit',
    doneButton: '.js-done',
    lat: '#event-form [name="lat"]',
    lng: '#event-form [name="lng"]',
    mapIdSmall: 'map-small',
    mapIdLarge: 'map-large',
    stateFailure: '.state.failure',
    stateNoResults: '.state.no-results',
    stateResults: '.state.results',
    stateSearching: '.state.searching'
};

var largeMap = null,
    smallMap = new EventMap({
        domId: dom.mapIdSmall,
        location: getEventLocation(),
        static: true
    });

$(dom.editButton).on('shown.bs.tab', onEdit);
$(dom.doneButton).on('click', onDone);

function onEdit() {
    if (largeMap === null) {
        largeMap = mapModule.create({
            domId: dom.mapIdLarge,
            location: getEventLocation(),
            crosshairs: true
        });
    } else {
        largeMap.setView(getEventLocation());
    }
}

function onDone() {
    var latLng = largeMap.getCenter();
    setEventLocation(latLng);
}

function setEventLocation(latLng) {
    smallMap.setLocation(latLng);
    $(dom.lat).val(latLng.lat);
    $(dom.lng).val(latLng.lng);
}

function getEventLocation() {
    var latLng = L.latLng(getFloatValue(dom.lat), getFloatValue(dom.lng));
    return latLng;
}

function getFloatValue(selector) {
    var value = $(selector).val();
    if (value) {
        value = parseFloat(value, 10);
    } else {
        value = 0;
    }
    return value;
}

function onSearching() {
    $(dom.addressSearchButton).addClass('disabled');
    $(dom.addressStates).hide();
    $(dom.stateSearching).show();
}

function onFailure(jqXHR, textStatus, error) {
    $(dom.addressSearchButton).removeClass('disabled');
    $(dom.addressStates).hide();
    $(dom.stateFailure).show();
    console.log('Unexpected geocode error: ' + textStatus + ' ' + error);
}

function onAddressFound(result) {
    $(dom.addressSearchButton).removeClass('disabled');
    $(dom.addressStates).hide();
    if (result.candidates.length === 1) {
        var candidate = result.candidates[0],
            lat = candidate.y,
            lng = candidate.x;
        zoomToCandidate(lng, lat);
    } else {
        showCandidates(result.candidates);
    }
}

function onAddressNotFound() {
    $(dom.addressSearchButton).removeClass('disabled');
    $(dom.addressStates).hide();
    $(dom.stateNoResults).show();
}

function showCandidates(candidates) {
    var $ul = $(dom.stateResults).find('ul');

    $(dom.stateResults).show();
    $ul.empty();

    for(var i = 0, count = candidates.length; i < count; i++) {
        var candidate = candidates[i],
            $el = $('<li><a href="javascript:;"></a></li>'),
            $anchor = $el.find('a');

        $anchor
            .text(candidate.address)
            .data({
                lat: candidate.y,
                lng: candidate.x
            });

        $ul.append($el);
    }
}

function zoomToCandidate(lng, lat) {
    var point = L.latLng(lat, lng);
    setEventLocation(point);
}

locationSearch({
    url: config.urls.geocode,
    $button: $(dom.addressSearchButton),
    $textbox: $(dom.addressField),
    searching: onSearching,
    found: onAddressFound,
    notFound: onAddressNotFound,
    failure: onFailure
});

$(dom.stateResults).on('click', 'li > a', function() {
    var lat = $(this).data('lat'),
        lng = $(this).data('lng');
    zoomToCandidate(lng, lat);
    $(dom.stateResults).hide();
});
