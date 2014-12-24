"use strict";

var $ = require('jquery'),
    fetchAndReplace = require('./fetchAndReplace');

var dom = {
    // Each container should contain either of these.
    followButton: '.btn-follow, .btn-unfollow',
    followButtonContainer: '.btn-follow-container'
};

$(dom.followButtonContainer).each(function(i, el) {
    var $container = $(el),
        $btn = $container.find(dom.followButton);
    fetchAndReplace({
        container: $container,
        target: $btn
    });
});
