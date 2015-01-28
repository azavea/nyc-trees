"use strict";

var $ = require('jquery'),
    Storage = require('./lib/storage');

var dom = {
    selections: '.quiz input:checked',
    activeQuestion: '.quiz .active.question'
};

function QuizProgress(slug) {
    return new Storage({
        key: 'quiz-progress-' + slug,
        getState: function() {
            var formData = {};
            $(dom.selections).each(function() {
                formData[$(this).attr('name')] = $(this).val();
            });
            return {
                form: formData,
                question: $(dom.activeQuestion).data('question')
            };
        },
        validate: function(state) {
            if (isNullOrUndefined(state)) {
                throw new Error('Unable to parse serialized state');
            }
            if (isNullOrUndefined(state.form)) {
                throw new Error('Expected `state.form` to exist');
            }
            if (!$.isNumeric(state.question)) {
                throw new Error('Expected `state.question` to be numeric');
            }
        }
    });
}

function isNullOrUndefined(value) {
    return value === null || typeof value === 'undefined';
}

module.exports = QuizProgress;
