"use strict";

var $ = require('jquery');

// Replaces the contents of `container` with the AJAX response content
// triggered by clicking on `target`.
//
// Options:
//
// target     Selector for the element that will trigger
//            the AJAX request.
//
// container  Selector for the element whose content will
//            be replaced and also contains `target`.
//
// onError    (Optional) AJAX error handler.
//
// The element selected by `target` must have a `data-url`
// attribute and supports an optional `data-verb` attribute
// that can be any of the acceptible values for the $.ajax
// `type` option.
//
// Returns a function that, when called, will remove the event
// handling.
function fetchAndReplace(options) {
    var domEventName = options.domEventName || 'click',
        handler = function(event) {
            var url = $(event.target).data('url'),
                verb = $(event.target).data('verb') || 'GET';
            if (url) {
                event.preventDefault();
                $.ajax(url, {
                        type: verb,
                        data: options.data
                    })
                    .done(function(content) {
                        $(options.container).html(content);
                    })
                    .fail(options.onError);
            }
        };

    $(options.container).on(domEventName, options.target, handler);
    return function() {
        $(options.container).off(domEventName, options.target, handler);
    };
}

// Expands `fetchAndReplace` by supporting multiple targets.
function fetchAndReplaceMany(options) {
    var targets = $(options.container).find(options.target),
        handlers = targets.map(function(i, el) {
            return fetchAndReplace($.extend({}, options, {
                target: options.target,
                container: $(el).parents(options.container)
            }));
    });
    return function() {
        $.each(handlers, function(i, remove) {
            remove();
        });
    };
}

module.exports = fetchAndReplaceMany;
