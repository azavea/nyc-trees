"use strict";

var SavedState = require('./lib/SavedState');

// We need to clear the currently selected blockfaces,
// since they have presumably been reserved
SavedState.clear('reserve-blockfaces');
