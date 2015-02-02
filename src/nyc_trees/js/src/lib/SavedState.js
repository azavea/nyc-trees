"use strict";

var $ = require('jquery'),
    storage = window.localStorage || {};

// Responsible for serializing and deserializing data to `localStorage`.
//
// Any valid JS object returned from `getState` will be stringified and
// saved to `localStorage` when the `save` function is invoked.
//
// Calling `load` will deserialize and return the current value from
// `localStorage`. If there is no current value, or if there was an error
// during deserialization, then `load` will return `false`.
//
// Example usage:
//
//     var cache = new SavedState({
//         key: 'cart',
//         getState: function() {
//             return { items: [...] };
//         }
//     });
//
//     var state = cache.load();
//     if (state) {
//         _.each(state.items, addToCart);
//     }
//
//     btnAddToCart
//         .doAction(addToCart)
//         .onValue(cache, 'save');
//
function SavedState(options) {
    var opts = $.extend({}, {
        key: '',
        getState: $.noop,
        validate: $.noop
    }, options);

    if (!opts.key) {
        throw new Error('The `key` option is required');
    }

    function save() {
        storage[opts.key] = serialize();
    }

    // Return false if there is no current value to load of if there was an
    // error validating the state.
    function load() {
        var state = deserialize(storage[opts.key]);
        if (state) {
            try {
                opts.validate(state);
            } catch (ex) {
                console.warn(ex);
                // State may have become corrupt or the data format may have
                // changed.
                clear();
                return false;
            }
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

module.exports = SavedState;
