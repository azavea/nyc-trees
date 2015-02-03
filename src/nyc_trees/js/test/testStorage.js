"use strict";
/* global suite */
/* global test */
/* global beforeEach */

var assert = require('chai').assert,
    Storage = require('../src/lib/Storage');

suite('Storage', function() {
    beforeEach(function() {
        localStorage.clear();
    });

    test('Loading/Saving', function() {
        var cache = new Storage({
            key: 'test',
            getState: function() {
                return {foo: 'bar'};
            }
        });

        // Nothing was saved yet so there's nothing to load.
        assert.isFalse(cache.load());

        cache.save();
        assert.deepEqual(cache.load(), {foo: 'bar'});
    });

    test('Invalid state gets cleared', function() {
        function makeCache(n, enableValidation) {
            return new Storage({
                key: 'test',
                getState: function() {
                    return n;
                },
                validate: function(state) {
                    if (enableValidation && state !== n) {
                        throw new Error('Expected state to be ' + n);
                    }
                }
            });
        }

        // Demonstrates what happens when 2 different storage objects share
        // the same key. As long as the data formats are similar, they can
        // be used interchangeably. But once validation is enabled (to simulate
        // different data structures), an exception will be thrown during
        // deserialization, and cause the storage object to be cleared.

        var cache1 = makeCache(1, false),
            cache2 = makeCache(2, false);

        assert.isFalse(cache1.load());
        assert.isFalse(cache2.load());

        cache1.save();
        assert.equal(cache1.load(), 1);
        assert.equal(cache2.load(), 1);

        cache2.save();
        assert.equal(cache1.load(), 2);
        assert.equal(cache2.load(), 2);

        // Reload storage objects with validation enabled.
        cache1 = makeCache(1, true);
        cache2 = makeCache(2, true);

        cache1.clear();
        cache2.clear();

        assert.isFalse(cache1.load());
        assert.isFalse(cache2.load());

        cache1.save();
        assert.equal(cache1.load(), 1);
        assert.isFalse(cache2.load());

        cache2.save();
        assert.equal(cache2.load(), 2);
        assert.isFalse(cache1.load());
    });
});
