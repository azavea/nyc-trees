"use strict";

var $ = require('jquery');

// Tab functions on jquery
require('bootstrap');

module.exports = function (tabList) {
    function changeTabToHash() {
        // Use hash to determine which tab to go to
        var hash = window.location.hash;
        if (hash) {
            $(tabList).find('a[href="' + hash + '"]').tab('show');
        }
    }
    changeTabToHash();

    // bootstrap swallows events so the url doesn't change
    // add our own here
    $(tabList).on('click', 'a', function (e) {
        $(this).tab('show');

        var originalScrollPosition = $('body').scrollTop();
        window.location.hash = this.hash;
        $('html,body').scrollTop(originalScrollPosition);
    });
    if ("onhashchange" in window) {
        $(window).on("hashchange", changeTabToHash);
    }
};
