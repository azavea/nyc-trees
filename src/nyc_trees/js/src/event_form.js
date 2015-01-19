"use strict";

require('bootstrap');

var Modernizr = require('modernizr'),
    $ = require('jquery'),
    L = require('leaflet'),
    eventMap = require('./event_map');

var dom = {
    useMyInfo: '#use-my-contact-info',
    userContactName: '#user-contact-name',
    userContactEmail: '#user-contact-email',
    eventContactName: '#event-form [name="contact_name"]',
    eventContactEmail: '#event-form [name="contact_email"]'
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

