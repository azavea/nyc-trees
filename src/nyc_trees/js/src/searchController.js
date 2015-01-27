"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    geocoder = require('./geocoder'),
    zoom = require('./mapUtil').zoom,
    setCenterAndZoomLL = require('./mapUtil').setCenterAndZoomLL;

module.exports = {create: create};

function locationSearch(options) {
    var $textbox = options.$textbox,
        $button = options.$button,
        searching = options.searching || $.noop,
        found = options.found || $.noop,
        notFound = options.notFound || $.noop,
        failure = options.failure || $.noop,
        geocode = geocoder(options.url),
        cache = {};

    $textbox.on('keypress', function(e){
        if (e.keyCode === 13) {
            $button.click();
        }
    });

    $button.on('click', function(e) {
        var address = $textbox.val().trim();
        if (!address) {
            return;
        }
        if (cache[address]) {
            found(cache[address]);
            return;
        }
        searching();
        geocode(address).done(function(data) {
            cache[address] = data;
            found(data);
        }).fail(function(jqXHR, textStatus, error) {
            if (!error || !error.superseded) {
                if (jqXHR.status === 404) {
                    notFound();
                } else {
                    failure(jqXHR, textStatus, error);
                }
            }
        });
    });
}

function create($controlsContainer, map) {
    var searchInProgress = false,

        $showSearchButton = $($('#template-map-search-toolbar-button').html()),

        $searchControlContainer = $($('#template-map-search').html()),

        $textbox = $searchControlContainer.find('.location-search-box'),
        $doSearchButton = $searchControlContainer.find('.location-search-button'),
        $status = $searchControlContainer.find('.location-search-status'),
        $closeSearchButton = $searchControlContainer.find('.location-search-close'),

        toggleSearch = function() {
            $showSearchButton.toggleClass('active');
            $searchControlContainer.toggle();
            if ($textbox.is(':visible')) {
                $textbox.focus().select();
            }
        },

        updateStatus = function(message, isSearching) {
            if (message) {
                $status.text(message).show();
            } else {
                $status.hide();
            }
            searchInProgress = !!isSearching;
        },

        addCandidateToList = function($list, $newItem, candidate) {
            $newItem.find('.location-address').text(candidate.address);
            $newItem.on('click', 'a',  function() {
                $list.find('a').off('click');
                $list.remove();
                zoomToCandidate(candidate);
            });
            $list.append($newItem);
        },

        showCandidates = function(candidates) {
            var $list = $($('#template-map-search-result-list').html()),
                $itemTemplate;
            updateStatus('Choose an address or search again');
            $searchControlContainer.find('.location-search-results').remove();
            $searchControlContainer.append($list);
            $itemTemplate = $searchControlContainer.find('.location-search-result');
            $searchControlContainer.find('.location-search-result').remove();

            for(var i = 0, count = candidates.length; i < count; i++) {
                addCandidateToList($list, $itemTemplate.clone(), candidates[i]);
            }
        },

        zoomToCandidate = function(candidate) {
            var point = L.latLng(candidate.y, candidate.x);
            setCenterAndZoomLL(map, zoom.NEIGHBORHOOD, point);
            updateStatus();
        },

        searching = function() {
            updateStatus('Searching...', true);
        },

        found = function(result) {
            if (result.candidates.length === 1) {
                zoomToCandidate(result.candidates[0]);
            } else {
                showCandidates(result.candidates);
            }
        },

        notFound = function() {
            updateStatus('Sorry, we could not find a location for that address.');
        },

        failure = function(jqXHR, textStatus, error) {
            updateStatus('Sorry, there was a problem finding that location.');
            console.log('Unexpected geocode error: ' + textStatus + ' ' + error);
        };

    $controlsContainer.prepend($showSearchButton);

    // Add the search box and related controls directly to the Leaflet
    // control container for easier styling
    $(map.getContainer()).find('.leaflet-control-container')
                         .prepend($searchControlContainer);

    locationSearch({
        url: config.urls.geocode,
        $button: $doSearchButton,
        $textbox: $textbox,
        searching: searching,
        found: found,
        notFound: notFound,
        failure: failure
    });

    $showSearchButton.on('click', toggleSearch);
    $closeSearchButton.on('click', toggleSearch);

    $textbox.on('keydown', function(e) {
        if (!searchInProgress) {
            updateStatus();
        }
    });
}
