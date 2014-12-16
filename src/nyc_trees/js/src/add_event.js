"use strict";

require('bootstrap');

var Modernizr = require('modernizr'),
    $ = require('jquery');

var dom = {
    useMyInfo: '#use-my-contact-info',
    userContactInfo: '#user-contact-info',
    userContactEmail: '#user-contact-email',
    eventContactInfo: '#event-form [name="contact_info"]',
    eventContactEmail: '#event-form [name="contact_email"]'
};

Modernizr.load({
    test: Modernizr.inputtypes.date && Modernizr.inputtypes.time,
    nope: config.files["datetimepicker_polyfill.js"]
});

$(dom.useMyInfo).on('click', function(e) {
    e.preventDefault();

    var userEmail = $(dom.userContactEmail).val(),
        userInfo = $(dom.userContactInfo).val();

    $(dom.eventContactEmail).val(userEmail);
    $(dom.eventContactInfo).val(userInfo);
});
