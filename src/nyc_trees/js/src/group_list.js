"use strict";

var $ = require('jquery'),
    fetchAndReplace = require('./fetchAndReplace'),
    attrs = {name: 'data-group-name',
             description: 'data-group-description'},
    dom = {searchInput: '[data-class="group-search"]',
           viewAll: '[data-class="group-view-all"]',
           searchNoneFound: '[data-class="group-search-none-found"]',
           groups: '[' + attrs.name + ']'},
    $groups,
    $searchNoneFound;

// Needed for Follow button event handlers.
require('./followGroupButton');

fetchAndReplace({
    container: '.btn-follow-container',
    target: '.btn-follow, .btn-unfollow'
});

$groups = $(dom.groups);
$searchNoneFound = $(dom.searchNoneFound);

$(dom.viewAll).on('click', function () {
    $groups.show();
    $(dom.viewAll).hide();
});

$(dom.searchInput).on('input', function (e) {
    var query = $(e.target).val(),
        noneFound = false;

    $(dom.viewAll).hide();

    if (query === '') {
        $groups.show();
    } else {
        noneFound = true;
        $.each($groups, function(__, group) {
            var $group = $(group),
                name = $group.attr(attrs.name),
                description = $group.attr(attrs.description);

            if (name.indexOf(query) !== -1 ||
                description.indexOf(query) !== -1) {
                $group.show();
                noneFound = false;
            } else {
                $group.hide();
            }
        });
    }

    if (noneFound === true) {
        $searchNoneFound.show();
    } else {
        $searchNoneFound.hide();
    }
});
