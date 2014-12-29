"use strict";
var $ = require('jquery'),
    fieldSelector = 'input[type=text],input[type=email],textarea';

module.exports = function() {
    $('form').eq(0).find(fieldSelector).eq(0).focus().select();
};
