"use strict";

var fetchAndReplace = require('./fetchAndReplace');

require('./event_list');

// Because onclick events are triggered for each defined target in the
// fetchAndReplace container, a target such as ".btn-approve, .btn-deny" will
// trigger 2 requests whenever either of the buttons are pressed.
// The workaround is to define a single target for each fetchAndReplace
// configuration.
fetchAndReplace({
    container: '.btn-grant-access-container',
    target: '.btn-approve'
});
fetchAndReplace({
    container: '.btn-grant-access-container',
    target: '.btn-deny'
});
