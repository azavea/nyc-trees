"use strict";

var $ = require('jquery'),
    fetchAndReplace = require('./fetchAndReplace'),
    attrs = {
        name: 'data-group-name',
        description: 'data-group-description',
        affiliation: 'data-affiliation'
    },
    dom = {
        searchInput: '[data-class="group-search"]',
        viewAll: '[data-class="group-view-all"]',
        searchNoneFound: '[data-class="group-search-none-found"]',
        groups: '[' + attrs.name + ']'
    },
    $groups,
    $searchNoneFound;

fetchAndReplace({
    container: '.btn-follow-container',
    target: '.btn-follow, .btn-unfollow',
    data: { 'render_follow_button_without_count': 'True' }
});

$groups = $(dom.groups);
$searchNoneFound = $(dom.searchNoneFound);

$(dom.viewAll).on('click', function () {
    $groups.show();
    $(dom.viewAll).hide();
});

$(dom.searchInput).on('input', function (e) {
    var query = $(e.target).val().toLowerCase(),
        noneFound = false;

    $(dom.viewAll).hide();

    if (query === '') {
        $groups.show();
    } else {
        noneFound = true;
        $.each($groups, function(__, group) {
            var $group = $(group),
                name = $group.attr(attrs.name),
                description = $group.attr(attrs.description),
                affiliation = $group.attr(attrs.affiliation);

            if (name.indexOf(query) !== -1 ||
                description.indexOf(query) !== -1 ||
                affiliation.indexOf(query) !== -1) {
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
