"use strict";

var $ = require('jquery'),
    dom = {container: '[data-class="training-flatpage-container"]',
           nextButton: '[data-class="training-flatpage-subpage-next"]',
           previousButton: '[data-class="training-flatpage-subpage-previous"]',
           acceptFeedbackButton: '[data-class="training-flatpage-subpage-accept-feedback"]',
           question: '[data-class="question"]',
           answer: '[data-class="answer"]'},
    $container = $(dom.container),
    $nextButton = $(dom.nextButton),
    $previousButton = $(dom.previousButton),
    $acceptFeedbackButton = $(dom.acceptFeedbackButton),
    $subpages = $container.children('div'),
    pageCount = $subpages.length,
    currentPage = 0;

function showSubpage($subpage, index) {
    var $exercise = $subpage.children('form');

    // fully initialize the subpage for viewing, including cleaning up
    // elements that may have been put out of order by previous actions
    // on this subpage.

    $acceptFeedbackButton.hide();

    if ($exercise.length === 0) {
        $nextButton.show();
    } else {
        $nextButton.hide();
    }

    if (index > 0) {
        $previousButton.show();
    } else {
        $previousButton.hide();
    }

    $exercise.children(dom.question).show();
    $exercise.siblings().show();

    $exercise.children(dom.answer).each(function (__, member) {
        var $member = $(member),
            $feedbackEl = $member.children('div'),
            $label = $member.children('label'),
            $input = $label.children('input');

        $member.show();
        $label.show();
        $feedbackEl.hide();

        // for brevity, these get set to radio, rather than forcing
        // the flatpage author to have set them for each one
        $input.attr('type', 'radio');

        $input.attr('checked', false);
        // use the index (currentPage) to make a unique
        // radio button group
        $input.attr('name', index);
    });

    $subpage.show();
}


function evaluateExerciseInput (event) {
    var $label = $(event.currentTarget),
        $input = $label.children('input'),
        $feedbackEl = $label.siblings('div'),
        $member = $label.parent(dom.answer),
        $exercise = $member.parent('form'),

        correctValue = $exercise.attr('data-correct-value');

    $exercise.children(dom.question).hide();
    $exercise.siblings().hide();

    $label.hide();
    $feedbackEl.show();
    $member.siblings().hide();
    $previousButton.hide();

    if ($input.attr('value') === correctValue) {
        $nextButton.show();
    } else {
        $acceptFeedbackButton.show();
    }
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

$container.on('click', 'label', evaluateExerciseInput);

$nextButton.on('click', function () {
    currentPage++;
    showPageOrStep();
});
$previousButton.on('click', function () {
    currentPage--;
    showPageOrStep();
});
$acceptFeedbackButton.on('click', showPageOrStep);

if (pageCount > 0) {
    showPageOrStep();
}
