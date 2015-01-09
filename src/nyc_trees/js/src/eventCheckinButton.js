"use strict";

var $ = require('jquery'),
    fetchAndReplace = require('./fetchAndReplace');

var dom = {
    // Each container should contain either of these.
    checkinButton: '.btn-checkin, .btn-checkout',
    checkinButtonContainer: '.btn-checkin-container'
};

$(dom.checkinButtonContainer).each(function(i, el) {
    var $container = $(el),
        $btn = $container.find(dom.checkinButton);
    fetchAndReplace({
        container: $container,
        target: $btn
    });
});
