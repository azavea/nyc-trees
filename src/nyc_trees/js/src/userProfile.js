"use strict";

var $ = require('jquery'),
    privacySettings = require('./privacySettings.js'),
    bindShowAllRowsHandlers = require('./bindShowAllRowsHandlers'),

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

bindShowAllRowsHandlers();
