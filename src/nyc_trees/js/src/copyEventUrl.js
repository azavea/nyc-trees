"use strict";

var $ = require('jquery');

var dom = {
    copyEventUrl: '.js-copy-event-url'
};

$(dom.copyEventUrl).click(function (e) {
    var eventUrl = $(e.target).data('event-url');
    window.prompt('Please manually copy the selected text:', eventUrl);
});

