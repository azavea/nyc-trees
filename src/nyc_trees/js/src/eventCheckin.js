"use strict";

var $ = require('jquery');

// Needed for Check-in button event handlers.
require('./eventCheckinButton');

var dom = {
    increaseRsvpLimitButton: '#increase-rsvp-limit',
    maxAttendees: '#max-attendees'
};

$(dom.increaseRsvpLimitButton).click(function() {
    var $el = $(this);
    $.ajax({
        url: $el.data('url'),
        type: $el.data('verb'),
        dataType: 'json'
    }).done(function(data) {
        if (data.max_attendees) {
            $(dom.maxAttendees).text(data.max_attendees);
        }
    });
});
