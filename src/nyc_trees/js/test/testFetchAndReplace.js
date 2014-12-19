"use strict";
/* global suite */
/* global test */
/* global beforeEach */
/* global after */
/* global afterEach */

var $ = require('jquery');
var assert = require('chai').assert;
var sinon = require('sinon');
var fetchAndReplace = require('../src/fetchAndReplace');

var fixtureId = '__fixture__';

function addFixture() {
    var fixture = '<div id="__container"><a id="__target" href="#" data-url="a_fake_url"></a></div>';

    removeFixture();
    $('<div>', {
        id: fixtureId,
        html: fixture
    }).appendTo($('body'));
}

function removeFixture() {
    $('#' + fixtureId).remove();
}

suite('fetchAndReplace Basics', function() {
    test('Ensure the function is exported', function() {
        assert.isFunction(fetchAndReplace, 'The module did not export a function');
    });
});

suite('fetchAndReplace AJAX', function() {
    var remove, ajaxStub;

    beforeEach(function() {
        addFixture();
        ajaxStub = sinon.stub($, 'ajax', function (url, options) {
            var d = $.Deferred();
            d.resolve(options.type + " " + url);
            return d.promise();
        });
        remove = fetchAndReplace({
            container: '#__container',
            target: '#__target'
        });
    });

    test('Clicking the trigger makes a request and replaces content', function(done) {
        $('#__target').trigger('click');
        setTimeout(function() {
            assert.equal($('#__container').html(), "GET a_fake_url");
            remove();
            done();
        }, 0);
    });

    test('Verb is read from target', function(done) {
        $('#__target').data('verb', 'POST');
        $('#__target').trigger('click');
        setTimeout(function() {
            assert.equal($('#__container').html(), "POST a_fake_url");
            remove();
            done();
        }, 0);
    });

    test('Missing url prevents AJAX request', function(done) {
        $('#__target').data('url', '');
        $('#__target').trigger('click');
        setTimeout(function() {
            assert.equal(ajaxStub.callCount, 0,
                '$.ajax should not be called when data-url is not set on the target');
            remove();
            done();
        }, 0);
    });

    afterEach(function() {
      $.ajax.restore();
      removeFixture();
    });

    after(function() {
        removeFixture();
    });
});
