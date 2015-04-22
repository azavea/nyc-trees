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
    hash = window.location.hash,
    $subpages = $container.children('div'),
    pageCount = $subpages.length,
    currentPage = 0,
    $currentPage;

function showSubpage() {
    var $subpage = $($subpages[currentPage]),
        $exercise = $subpage.children('form'),
        index = currentPage;

    window.scrollTo(0, 0);

    $subpages.hide();

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

    // images should *not* be placed inside question forms unless they
    // are placed inside a question div. However, this is a safeguard
    // because the spec is not crystal clear and failing to show images
    // on question reload could be difficult to discover during testing
    $exercise.children('img').show();

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
        showSubpage();
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

// ids can be put on any element at or below the outermost
// subpage div and then linked to using the hash string
// if subpage children have the id, then the page will
// scroll to that element
// (tested in chrome and firefox)
if (hash !== "") {
    if ($container.find(hash).length > 0) {
        for (; currentPage < $subpages.length; currentPage++) {
            $currentPage = $($subpages[currentPage]);
            if ($currentPage.is(hash) ||
                $currentPage.find(hash).length > 0) {
                showSubpage();
                break;
            }
        }
    }
}
