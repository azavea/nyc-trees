"use strict";

var $ = require('jquery');

var POLL_INTERVAL_MS = 5000;

// Polls the 'pollUrl' endpoint until the 'check' callback returns true
module.exports = function(pollUrl, check) {
    function poll() {
        $.ajax(pollUrl, {
            cache: false,
            dataType: 'json'
        })
        .done(function(data) {
            if (! check(data)) {
                retry();
            }
        })
        .fail(retry);
    }

    function retry() {
        setTimeout(poll, POLL_INTERVAL_MS);
    }

    return poll;
};
