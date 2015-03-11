"use strict";

var $ = require('jquery');

var dom = {
    mapAnotherPopup: '#map-another-popup',
    possibleContent: '[data-class="map-another-possible"]',
    impossibleContent: '[data-class="map-another-impossible"]'
};

module.exports = {
    show: function(responseContent) {
        var $el = $(dom.mapAnotherPopup);

        $el.modal('show');

        if (responseContent.noMoreReservations) {
            $el.find(dom.possibleContent).addClass('hidden');
            $el.find(dom.impossibleContent).removeClass('hidden');
        } else {
            $el.find(dom.possibleContent).removeClass('hidden');
            $el.find(dom.impossibleContent).addClass('hidden');
        }

    }
};
