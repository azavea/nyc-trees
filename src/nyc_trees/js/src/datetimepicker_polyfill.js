"use strict";

var $ = require('jquery'),
    Modernizr = require('modernizr');

require('bootstrap');
require('bootstrap-datetimepicker');

if (! Modernizr.inputtypes.date) {
    $('input[type="date"]').datetimepicker({pickTime: false});
}

if (! Modernizr.inputtypes.time) {
    $('input[type="time"]').datetimepicker({pickDate: false});
}

if (! Modernizr.inputtypes.datetime) {
    $('input[type="datetime"]').datetimepicker();
}
