"use strict";

var $ = require('jquery');

var dom = {
    mapAnotherPopup: '#map-another-popup',
    possibleContent: '[data-class="map-another-possible"]',
    impossibleContent: '[data-class="map-another-impossible"]',
    goButton: "#map-another-go-button",
    groupSlugAttr: 'data-group-slug',
    eventSlugAttr: 'data-event-slug'
};

module.exports = {
    getQueryStringPassAlong: function () {
        var $goButton = $(dom.goButton),
            groupSlug = $goButton.attr(dom.groupSlugAttr),
            eventSlug = $goButton.attr(dom.eventSlugAttr);

        return eventSlug && groupSlug ?
            '?group_slug=' + groupSlug + '&event_slug=' + eventSlug : "";
    },

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
