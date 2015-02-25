"use strict";

var $ = require('jquery'),
    util = require('./util'),
    SavedState = require('./SavedState');

// Factory functions for various states.

module.exports = {
    quizProgressState: function(slug) {
        return new SavedState({
            key: 'quiz-progress-' + slug,
            validate: function(state) {
                if (util.isNullOrUndefined(state)) {
                    throw new Error('Unable to parse serialized state');
                }
                if (util.isNullOrUndefined(state.form)) {
                    throw new Error('Expected `state.form` to exist');
                }
                if (!$.isNumeric(state.question)) {
                    throw new Error('Expected `state.question` to be numeric');
                }
            }
        });
    },

    quizSubmissionState: function(slug) {
        return new SavedState({
            key: 'quiz-submission-' + slug,
            validate: function(state) {
                if (!$.isArray(state)) {
                    throw new Error('Expected `state` to be an array');
                }
            }
        });
    }
};
