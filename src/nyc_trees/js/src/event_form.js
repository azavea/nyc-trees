"use strict";

require('bootstrap');

var Modernizr = require('modernizr'),
    $ = require('jquery'),
    L = require('leaflet'),
    mapModule = require('./map');

var dom = {
    useMyInfo: '#use-my-contact-info',
    userContactName: '#user-contact-name',
    userContactEmail: '#user-contact-email',
    eventContactName: '#event-form [name="contact_name"]',
    eventContactEmail: '#event-form [name="contact_email"]',
    lat: '#event-form [name="lat"]',
    lng: '#event-form [name="lng"]',
    mapIdSmall: 'map-small',
    mapIdLarge: 'map-large'
};

Modernizr.load({
    test: Modernizr.inputtypes.date && Modernizr.inputtypes.time,
    nope: config.files["datetimepicker_polyfill.js"]
});

$(dom.useMyInfo).on('click', function(e) {
    e.preventDefault();

    var userEmail = $(dom.userContactEmail).val(),
        userContactName = $(dom.userContactName).val();

    $(dom.eventContactEmail).val(userEmail);
    $(dom.eventContactName).val(userContactName);
});

mapModule.create({
    domId: dom.mapIdSmall,
    location: L.latLng(getFloatValue(dom.lat), getFloatValue(dom.lng)),
    static: true
});

function getFloatValue(selector) {
    var value = $(selector).val();
    if (value) {
        value = parseFloat(value, 10);
    } else {
        value = 0;
    }
    return value;
}