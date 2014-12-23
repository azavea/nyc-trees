"use strict";

var $ = require('jquery'),
    privacySettings = require('./privacySettings.js'),

    dom = {
        form: '#form'
    };

$(dom.form).on('submit', function () {
    privacySettings.prepareForSave();
});

// Note that "Cancel" is handled by reloading the page so we don't need to do anything
