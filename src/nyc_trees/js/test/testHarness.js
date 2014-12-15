"use strict";
/* global suite */
/* global test */

var assert = require('chai').assert;

suite('Harness test', function() {
    test('Ensure the test harness is working', function() {
        assert.equal(1, 1);
    });
});
