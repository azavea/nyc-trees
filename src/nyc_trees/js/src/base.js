"use strict";

var $ = require('jquery'),
    csrf = require('./csrf');

// Place JS here if it needs to be executed on every page.
require('bootstrap');

$.ajaxSetup(csrf.jqueryAjaxSetupOptions);
