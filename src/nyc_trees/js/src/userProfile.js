"use strict";

var $ = require('jquery'),
    privacySettings = require('./privacySettings.js'),

    dom = {
        privacyForm: '#privacy-form',
        cancelButton: '.js-cancel'
    };

$(dom.privacyForm).on('submit', function () {
    privacySettings.prepareForSave();
    // Note: postback rather than ajax update because changing privacy settings
    // may affect how the user profile template is rendered.
});

$(dom.cancelButton).on('click', function () {
    privacySettings.revert();
});

$('[data-class="user-profile-groups-show-all"]').on('click', function (e) {
    e.preventDefault();
    $('[data-class="user-profile-group-row"]').show();
    $(e.target).hide();
});
