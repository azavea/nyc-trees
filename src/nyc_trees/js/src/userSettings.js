"use strict";

var $ = require('jquery'),
    privacySettings = require('./privacySettings.js'),

    dom = {
        form: '#form'
    };

$(dom.form).on('submit', function () {
    privacySettings.prepareForSave();
});

require('./lib/tabhash/')('#user-settings-tabs');

// Note that "Cancel" is handled by reloading the page so we don't need to do anything
