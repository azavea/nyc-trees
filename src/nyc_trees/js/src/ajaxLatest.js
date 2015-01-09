"use strict";

var $ = require('jquery');

/*

This module builds an "interruptible" ajax function that only delivers
a successful response for the most recent request.

NOTE: The implementation only supports promises, not callbacks.

Usage:

var ajaxLatest = require('./ajaxLatest'),
    defaultOptions = {
        url: '/some/endpoint,
        type: 'GET',
        dataType: 'json'
    },
    ajax = ajaxLatest(defaultOptions);

    ajax({data:{q:'millennium falcon'}}).done(function(data){
        alert(data);
    }).fail(function(jqXhr, errorText, error){
        if (error && error.superseded) {
          // fail silently, since another request took over
        } else {
          // handle the real ajax error
        }
    });

*/

module.exports = function(defaultOptions) {
    var requests = [],
        deferreds = [],
        isMostRecent = function(request) {
            if (requests.length) {
                return requests[requests.length - 1] === request;
            } else {
                return false;
            }
        },
        actOn = function(request, fn) {
            var interruptMessage = 'Another request interupted this one.';
            while (requests.length) {
                var req = requests.pop(),
                    def = deferreds.pop();
                if (req === request) {
                    fn(def);
                } else {
                    req.abort();
                    def.reject(req, interruptMessage, {
                        superseded: true,
                        error: interruptMessage
                    });
                }
            }
        };

    return function(options) {
        var request = $.ajax($.extend({}, defaultOptions, options)),
            deferred = $.Deferred();
        requests.push(request);
        deferreds.push(deferred);

        request.done(function(data) {
            if (isMostRecent(request)) {
                actOn(request, function(def) {
                    def.resolve(data);
                });
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            if (isMostRecent(request)) {
                actOn(request, function(def) {
                    def.reject(jqXHR, textStatus, errorThrown);
                });
            }
        });

        return deferred;
    };
};
