"use strict";

var $ = require('jquery');

var dom = {
    pollUrl: '#poll-url',
    checkedIn: '#checked-in',
    notCheckedIn: '#not-checked-in'
};

var POLL_INTERVAL_MS = 5000,
    pollUrl = $(dom.pollUrl).val();

function poll() {
    $.ajax(pollUrl, {
        cache: false,
        dataType: 'json'
    })
    .done(function(data) {
        if (data && data.checked_in) {
            $(dom.notCheckedIn).addClass('hidden');
            $(dom.checkedIn).removeClass('hidden');
        } else {
            retry();
        }
    })
    .fail(retry);
}

function retry() {
    setTimeout(poll, POLL_INTERVAL_MS);
}

poll();
