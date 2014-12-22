"use strict";

var $ = require('jquery');

$('[data-class="user-profile-groups-show-all"]').on('click', function (e) {
    e.preventDefault();
    $('[data-class="user-profile-group-row"]').show();
    $(e.target).hide();
});
