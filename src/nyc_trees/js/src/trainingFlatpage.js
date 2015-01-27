"use strict";

var $ = require('jquery'),
    dom = {container: '[data-class="training-flatpage-container"]',
           trainingSubpage: 'div',
           nextButton: '[data-class="training-flatpage-subpage-next"]'},
    $container = $(dom.container),
    $subpages = $container.find(dom.trainingSubpage),
    pageCount = $subpages.length,
    $nextButton = $(dom.nextButton),
    currentPage = 0;

function showPageOrStep() {
    if (currentPage < pageCount) {
        $subpages.hide();
        $($subpages[currentPage]).show();
        currentPage++;
    } else {
        window.location.href = $nextButton.attr('data-href');
    }
}

// container starts hidden so that subpages won't appear before
// this js has a chance to hide them
$subpages.hide();
$container.show();

$nextButton.on('click', showPageOrStep);

if (pageCount > 0) {
    showPageOrStep();
}
