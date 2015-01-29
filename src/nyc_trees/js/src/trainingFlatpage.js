"use strict";

var $ = require('jquery'),
    dom = {container: '[data-class="training-flatpage-container"]',
           nextButton: '[data-class="training-flatpage-subpage-next"]',
           previousButton: '[data-class="training-flatpage-subpage-previous"]'},
    $container = $(dom.container),
    $nextButton = $(dom.nextButton),
    $previousButton = $(dom.previousButton),
    $subpages = $container.children('div'),
    pageCount = $subpages.length,
    currentPage = 0;

function showSubpage($subpage, index) {
    if (index > 0) {
        $previousButton.show();
    } else {
        $previousButton.hide();
    }

    $subpage.show();
}

function showPageOrStep() {
    if (currentPage < pageCount) {
        $subpages.hide();
        showSubpage($($subpages[currentPage]), currentPage);
    } else {
        window.location.href = $nextButton.attr('data-href');
    }
}

// container starts hidden so that subpages won't appear before
// this js has a chance to hide them
$subpages.hide();
$container.show();

$nextButton.on('click', function () {
    currentPage++;
    showPageOrStep();
});
$previousButton.on('click', function () {
    currentPage--;
    showPageOrStep();
});

if (pageCount > 0) {
    showPageOrStep();
}
