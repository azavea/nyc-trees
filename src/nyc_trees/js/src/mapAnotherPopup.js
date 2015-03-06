"use strict";

var $ = require('jquery');

var dom = {
        mapAnotherPopup: '#map-another-popup'
};

module.exports = {
    show: function() {
        $(dom.mapAnotherPopup).modal('show');
    }
};
