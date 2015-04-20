"use strict";

// copied from OTM2, see:
// https://github.com/OpenTreeMap/OTM2/blob/2fec7c9b2ae39864b4cae0ee4953febc1abb59ba/opentreemap/treemap/js/src/statePrompter.js

var _locked,
    _warning,
    _question,
    _externalBeforeUnload;

function lock () {
    if (_locked === false) {
        _locked = true;
        // don't clobber onbeforeunload in case it's used elsewhere
        _externalBeforeUnload = window.onbeforeunload || null;
        window.onbeforeunload = function () { return _warning; };
    }
}

function unlock () {
    if (_locked === true) {
        _locked = false;
        window.onbeforeunload = _externalBeforeUnload || null;
    }
}

function canProceed() {
    // if a runmode in the app has turned on the lock, prompt before continuing
    // this function can be used inside any function that will change runmodes
    // and it resembles the behavior of window.onbeforeunload
    return _locked === true ?
        window.confirm(_warning + ' ' + _question) : true;
}

exports.init = function (options) {

    if (_warning || _question) {
        throw ("Cannot initialize module multiple times.");
    }

    _locked = false;
    _warning = options.warning;
    _question = options.question;

    return {
        canProceed: canProceed,
        unlock: unlock,
        lock: lock
    };
};
