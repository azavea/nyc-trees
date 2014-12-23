'use strict';

var $ = require('jquery');

$('.nav-menubutton').on('click', function (a) {
    $('body').toggleClass('menu-active');
});
