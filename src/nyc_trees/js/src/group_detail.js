"use strict";

var fetchAndReplace = require('./fetchAndReplace');

fetchAndReplace({
    container: '.btn-follow-container',
    target: '.btn-follow, .btn-unfollow'
});

require('./event_list');
