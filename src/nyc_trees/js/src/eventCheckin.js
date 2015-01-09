"use strict";

var $ = require('jquery'),
    fetchAndReplace = require('./fetchAndReplace');

var dom = {
    increaseRsvpLimitButton: '#increase-rsvp-limit'
};

fetchAndReplace({
    container: '.btn-checkin-container',
    target: '.btn-checkin, .btn-checkout'
});

$(dom.increaseRsvpLimitButton).click(function() {
    var $el = $(this);
    $.ajax({
        url: $el.data('url'),
        type: $el.data('verb'),
        dataType: 'json'
    }).done(function(data) {
        if (data.max_attendees) {
            var text = $el.data('text') + ' (' + data.max_attendees + ')';
            $el.text(text);
        }
    });
});
