var $ = require('jquery');

require('bootstrap');
require('bootstrap-datetimepicker');

Modernizr = require('modernizr');

if (! Modernizr.inputtypes.date) {
    $('input[type="date"]').datetimepicker({pickTime: false});
}

if (! Modernizr.inputtypes.time) {
    $('input[type="time"]').datetimepicker({pickDate: false});
}

if (! Modernizr.inputtypes.datetime) {
    $('input[type="datetime"]').datetimepicker();
}
