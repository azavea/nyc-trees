"use strict";

var $ = require('jquery');

var dom = {
    toggleField: '[data-toggle-field]'
};

$(dom.toggleField).click(function(e) {
    var checked = $(this).prop('checked'),
        toggleFieldSel = $(this).data('toggle-field'),
        $target = $(toggleFieldSel);
    $target.toggleClass('hidden', !checked);
});
