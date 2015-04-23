"use strict";

var $ = require('jquery'),
    states = require('./lib/states');

var dom = {
    quizSlug: '[name="quiz-slug"]',
    userId:  '[name="user-id"]',
    correctAnswers: '[name="correct-answers"]'
};

function saveCorrectAnswers() {
    var slug = $(dom.quizSlug).val(),
        userId = $(dom.userId).val(),
        progress = states.quizSubmissionState(slug, userId),
        newState = numberArray($(dom.correctAnswers).val().split(','));
    progress.save(newState);
}

function numberArray(arr) {
    return arr.map(parseIntBase10).filter($.isNumeric);
}

function parseIntBase10(n) {
    return parseInt(n, 10);
}

// Reset quiz progress back to the first question.
function resetQuizProgress() {
    var slug = $(dom.quizSlug).val(),
        userId = $(dom.userId).val(),
        progress = states.quizProgressState(slug, userId),
        state = progress.load();
    if (state) {
        progress.save($.extend(state, {
            question: 0
        }));
    }
}

saveCorrectAnswers();
resetQuizProgress();
