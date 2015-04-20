"use strict";

var $ = require('jquery'),

    dom = {
        fileChooser: 'input[type="file"]',
        submitButton: 'button[type="submit"]'
    };

$(dom.fileChooser).on('change', function () {
    $(dom.submitButton).prop('disabled', false);
});


