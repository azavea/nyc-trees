"use strict";

var $ = require('jquery'),
    csrf = require('./csrf');

// Place JS here if it needs to be executed on every page.
require('bootstrap');

$.ajaxSetup(csrf.jqueryAjaxSetupOptions);

// Enable the sliding menu
$('.nav-menubutton').on('click', function (a) {
    $('body').addClass('menu-active');
});

$('.overlay-menued').on('click', function (a) {
    $('body').removeClass('menu-active');
});

if ('ontouchstart' in window) {
  /* cache dom references */ 
  var $body = $('body'); 

  /* bind events */
  $(document).ready(function() {
      $body.addClass('fixfixed');
  });
}