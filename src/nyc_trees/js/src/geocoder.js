"use strict";

var ajaxLatest = require('./ajaxLatest');

module.exports = function(url) {
    var ajax = ajaxLatest({
        url: url,
        type: 'GET',
        dataType: 'json'
    });
    return function(address) {
        return ajax({data: {address: address}});
    };
};
