"use strict";

var $ = require('jquery');

var dom = {
    mapAnotherPopup: '#map-another-popup',
    possibleContent: '[data-class="map-another-possible"]',
    impossibleContent: '[data-class="map-another-impossible"]',
    noMoreReservationsAttr: 'data-no-more-reservations'
};

module.exports = {
    show: function() {
        var $el = $(dom.mapAnotherPopup),
            noMoreReservations = $el.attr(dom.noMoreReservationsAttr) === 'True';

        $el.modal('show');

        if (noMoreReservations) {
            $el.find(dom.possibleContent).addClass('hidden');
            $el.find(dom.impossibleContent).removeClass('hidden');
        } else {
            $el.find(dom.possibleContent).removeClass('hidden');
            $el.find(dom.impossibleContent).addClass('hidden');
        }

    }
};
