"use strict";

var $ = require('jquery'),
    mapModule = require('../map');

var dom = {
        legendModal: '#legend',
        toggleLegend: '.legend-button'
    },
    $legendModal= $(dom.legendModal),
    helpShown = ('True' === mapModule.getDomMapAttribute('help-shown'));

if (!helpShown) {
    // Help hasn't been shown yet, so show it on page load
    $legendModal.modal('show');

    // When legend is closed, Show notification of how to re-open it
    $legendModal.one('hidden.bs.modal', onCloseLegend);
}

function onCloseLegend(e) {
    $(dom.toggleLegend).append(
        '<div class="legend-help">Go&nbsp;back&nbsp;to&nbsp;the help&nbsp;information.</div>'
    );
    // Hide notification on any click
    $(document).one('click', function () {
        $('.legend-help').hide();
    });
}
