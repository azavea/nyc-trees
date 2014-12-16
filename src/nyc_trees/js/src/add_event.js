"use strict";

require('bootstrap');

var Modernizr = require('modernizr'),
    $ = require('jquery');

Modernizr.load({
    test: Modernizr.inputtypes.date && Modernizr.inputtypes.time,
    nope: config.files["datetimepicker_polyfill.js"]
});
