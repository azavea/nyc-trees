"use strict";

var $ = require('jquery'),
    poller = require('./lib/poller');

var dom = {
    pollUrl: '#poll-url',
    checkedIn: '#checked-in',
    notCheckedIn: '#not-checked-in'
};

var POLL_INTERVAL_MS = 5000,
    pollUrl = $(dom.pollUrl).val(),

    poll = poller(pollUrl, function(data) {
        if (data && data.checked_in) {
            $(dom.notCheckedIn).addClass('hidden');
            $(dom.checkedIn).removeClass('hidden');
            return true;
        }
        return false;
    });

poll();
