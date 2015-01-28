"use strict";

var $ = require('jquery'),
    storage = window.localStorage || {};


function Storage(options) {
    var opts = $.extend({}, {
        key: '',
        getState: $.noop,
        validate: $.noop
    }, options);

    if (!!opts.key) {
        throw new Error('The `key` option is required');
    }

    function save() {
        storage[opts.key] = serialize();
    }

    function load() {
        var state = deserialize(storage[opts.key]);
        if (state) {
            opts.validate(state);
        }
        return state;
    }

    function clear() {
        delete storage[opts.key];
    }

    function serialize() {
        return opts.getState === $.noop ? '' :
            JSON.stringify(opts.getState());
    }

    // Return false if there was an error during deserialization.
    function deserialize(serializedState) {
        try {
            return JSON.parse(serializedState);
        } catch (ex) {
            // Ignore possible SyntaxError.
        }
        return false;
    }

    return {
        save: save,
        load: load,
        clear: clear
    };
}

module.exports = Storage;
