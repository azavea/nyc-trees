"use strict";

var $ = require('jquery'),
    util = require('./util'),
    SavedState = require('./SavedState');

// Factory functions for various states.

module.exports = {
    quizProgressState: function(slug, userId) {
        return new SavedState({
            key: 'quiz-progress-' + slug + '-user-' + userId,
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

    quizSubmissionState: function(slug, userId) {
        return new SavedState({
            key: 'quiz-submission-' + slug + '-user-' + userId,
            validate: function(state) {
                if (!$.isArray(state)) {
                    throw new Error('Expected `state` to be an array');
                }
            }
        });
    }
};
