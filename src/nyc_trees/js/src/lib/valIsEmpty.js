"use strict";

var $ = require('jquery');

module.exports = function valIsEmpty(selector) {
    return !$.trim($(selector).val());
};
