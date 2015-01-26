"use strict";

var $ = require('jquery'),
    storage = window.localStorage || {};

var dom = {
    selections: '.quiz input:checked',
    activeQuestion: '.quiz .active.question'
};

function QuizProgress(slug) {
    var key = 'quiz-progress-' + slug;

    function save() {
        storage[key] = serialize();
    }

    // Return restored quiz state.
    function restore() {
        var serializedData = storage[key],
            state = serializedData && serializedData.length > 0 ?
                        deserialize(serializedData) : {};
        return state;
    }

    // Delete serialized data from storage.
    function clear() {
        delete storage[key];
    }

    // Return current state of quiz.
    function getState() {
        return {
            form: $(dom.selections).serialize(),
            question: $(dom.activeQuestion).data('question') || 0
        };
    }

    // Return quiz selections and active question serialized into a string.
    function serialize() {
        return JSON.stringify(getState());
    }

    // Deserialize quiz state object.
    function deserialize(serializedState) {
        var state;
        try {
            state = JSON.parse(serializedState);
        } catch (ex) {
            // Ignore possible SyntaxError.
        }

        // Assertions.
        if (isNullOrUndefined(state)) {
            throw new Error('Unable to parse serialized state');
        }
        if (isNullOrUndefined(state.form)) {
            throw new Error('Expected `state.form` to exist');
        }
        if (!$.isNumeric(state.question)) {
            throw new Error('Expected `state.question` to be numeric');
        }

        // Expected format: "question.0=1&question.1=0&question.2=0..."
        var formData = {};
        $.each(state.form.split('&'), function(i, item) {
            var parts = item.split('=');
            formData[parts[0]] = parts[1];
        });
        state.form = formData;

        return state;
    }

    return {
        save: save,
        restore: restore,
        clear: clear
    };
}

function isNullOrUndefined(value) {
    return value === null || typeof value === 'undefined';
}

module.exports = QuizProgress;
