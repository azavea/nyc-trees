"use strict";

require('bootstrap');

var $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map'),
    EventMap = require('./EventMap');

var dom = {
    editButton: '.js-edit',
    doneButton: '.js-done',
    lat: '#event-form [name="lat"]',
    lng: '#event-form [name="lng"]',
    mapIdSmall: 'map-small',
    mapIdLarge: 'map-large'
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