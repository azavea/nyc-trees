"use strict";
/* global suite */
/* global test */

var $ = require('jquery'),
    assert = require('chai').assert,
    util = require('../src/lib/util');

suite('Utility functions', function() {
    test('isNullOrUndefined', function() {
        var foo, baz = {};

        assert.isTrue(util.isNullOrUndefined(null));
        assert.isTrue(util.isNullOrUndefined(undefined));
        assert.isTrue(util.isNullOrUndefined(foo));
        assert.isTrue(util.isNullOrUndefined(baz.bar));

        assert.isFalse(util.isNullOrUndefined(0));
        assert.isFalse(util.isNullOrUndefined(1));
        assert.isFalse(util.isNullOrUndefined(NaN));
        assert.isFalse(util.isNullOrUndefined(''));
        assert.isFalse(util.isNullOrUndefined(true));
        assert.isFalse(util.isNullOrUndefined(false));
    });
});
