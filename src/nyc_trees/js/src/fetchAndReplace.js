"use strict";

var $ = require('jquery');

/*
options is an Object with two required properties:
  target: A selector for the element that will trigger
          the AJAX request
  container: A selector for the element whose content will
             be replaced and also contains ``target``.

The element selected by ``target`` must have a ``data-url``
attribute and supports an optional ``data-verb`` attribute
that can be any of the acceptible values for the $.ajax
``type`` option.

Returns a function that, when called, will remove the event
handling.

*/

module.exports = function(options) {
    var domEventName = options.domEventName || 'click',
        handler = function(event) {
            var url = $(event.target).data('url'),
                verb = $(event.target).data('verb') || 'GET';
            if (url) {
                event.preventDefault();
                $.ajax(url, { type: verb }).done(function(content) {
                    $(options.container).html(content);
                }).fail(options.onError);
            }
        };

    $(options.container).on(domEventName, options.target, handler);
    return function() { $(options.container).off(domEventName, options.target, handler); };
};
