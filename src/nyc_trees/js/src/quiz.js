"use strict";

var $ = require('jquery');

var dom = {
    warning: '.quiz .active .alert',
    next: '.quiz .next',
    prev: '.quiz .prev',
    submit: '.quiz .submit'
};

function next(e) {
    /*jshint validthis:true */
    var id = +$(this).data('question');
    if (validate(id)) {
        hide(id);
        show(id + 1);
    }
}

function prev(e) {
    /*jshint validthis:true */
    var id = +$(this).data('question');
    hide(id);
    show(id - 1);
}

function submit(e) {
    /*jshint validthis:true */
    var id = +$(this).data('question');
    if (!validate(id)) {
        e.preventDefault();
    }
}

// Return true if there is 1 checked answer for given question.
function validate(id) {
    var selectedAnswer = $('[name="question.' + id + '"]:checked');
    if (selectedAnswer.size() === 1) {
        $(dom.warning).addClass('hidden');
        return true;
    }
    $(dom.warning).removeClass('hidden');
    return false;
}

function hide(id) {
    $('[data-question=' + id + ']').addClass('hidden');
    $('[data-question=' + id + ']').removeClass('active');
}

function show(id) {
    $('[data-question=' + id + ']').removeClass('hidden');
    $('[data-question=' + id + ']').addClass('active');
}

$(dom.next).click(next);
$(dom.prev).click(prev);
$(dom.submit).click(submit);
