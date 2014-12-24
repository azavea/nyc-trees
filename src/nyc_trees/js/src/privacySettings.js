"use strict";

// Manage toggle buttons for a set of privacy categories.
// Toggle state is kept in a DOM data attribute on each button.
// prepareForSave() copies that state to corresponding hidden form fields.
// revert() loads state from the hidden form fields.

var $ = require('jquery'),
    dom = {
        row: 'tr',
        privacyTogglers: '.privacy-toggler',
        lockIconClass: 'icon-lock'
    };

module.exports = {
    prepareForSave: loadDomStateFromHiddenFields,
    revert: loadHiddenFieldsFromDomState
};

loadHiddenFieldsFromDomState();
updateUI();
$(dom.privacyTogglers).on('click', togglePrivacy);

function togglePrivacy(e) {
    var $toggler = $(e.target),
        $row = $toggler.closest(dom.row);
    if (!$row.hasClass('disabled')) {
        var iAmNowPublic = !isPublic($toggler),
            $togglers = $(dom.privacyTogglers),
            isFirst = ($toggler[0] === $togglers[0]);
        setIsPublic($toggler, iAmNowPublic);
        if (isFirst && !iAmNowPublic) {
            // Making first row private makes all rows private
            setIsPublic($togglers, false);
        }
        updateUI();
    }
}

function updateUI() {
    var $togglers = $(dom.privacyTogglers),
        disable = ! isPublic($togglers.first());
    $togglers.each(function (i, toggler) {
        var $toggler = $(toggler),
            fieldName = $toggler.data('privacy-field-name'),
            $target = $('[data-privacy-toggle-target="' + fieldName + '"]'),
            iAmPublic = isPublic($toggler),
            $row = $toggler.closest(dom.row),
            $lockIcon = $row.find(dom.lockIcon);
        $toggler.html(iAmPublic ? 'Public' : 'Private');
        $target.toggleClass(dom.lockIconClass, !iAmPublic);  // hide lock icon when public
        if (i > 0) {
            $row.toggleClass('disabled', disable);
        }
    });
}

function loadDomStateFromHiddenFields() {
        $(dom.privacyTogglers).each(function () {
        var $toggler = $(this),
            iAmPublic = isPublic($toggler),
            $hidden = getHiddenForToggler($toggler);
        $hidden.val(iAmPublic ? 'True' : 'False');
    });
}

function loadHiddenFieldsFromDomState() {
    $(dom.privacyTogglers).each(function () {
        var $toggler = $(this),
            $hidden = getHiddenForToggler($toggler),
            iAmPublic = ($hidden.val() == 'True');
        setIsPublic($toggler, iAmPublic);
    });
    updateUI();
}

function isPublic($toggler) {
    return $toggler.data('is-public');
}

function setIsPublic($toggler, isPublic) {
    $toggler.data('is-public', isPublic);
}

function getHiddenForToggler($toggler) {
    var fieldName = $toggler.data('privacy-field-name'),
        $hidden = $('input[name=' + fieldName + ']');
    return $hidden;
}
