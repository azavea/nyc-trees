"use strict";

var zoom = {
    NEIGHBORHOOD: 16,
    MAX: 19
};

module.exports = {
    zoom: Object.freeze ? Object.freeze(zoom) : zoom,

    setCenterAndZoomLL: function(map, zoom, location) {
        // Never zoom out, or try to zoom farther than allowed.
        var zoomToApply = Math.max(
            map.getZoom(),
            Math.min(zoom, map.getMaxZoom()));

        map.setView(location, zoomToApply);
    }
};
