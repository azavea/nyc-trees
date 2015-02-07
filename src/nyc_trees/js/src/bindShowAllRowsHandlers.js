"use strict";

var $ = require('jquery');

var clickableSelector = '[data-class="show-all-list-rows"]';

module.exports = function() {
    $(clickableSelector).on('click', function (e) {
        var $target = $(e.target).parents(clickableSelector),
            rowDataClass = $target.attr('data-row-data-class');
        if (!rowDataClass) { return; }
        e.preventDefault();
        $('[data-class="' + rowDataClass + '"]').show();
        $target.hide();
    });
};
