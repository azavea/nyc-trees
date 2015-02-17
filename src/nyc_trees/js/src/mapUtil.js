"use strict";

var _ZOOM = {
    NEIGHBORHOOD: 16,
    MAX: 19
};

module.exports = {
    ZOOM: Object.freeze ? Object.freeze(_ZOOM) : _ZOOM,

    setCenterAndZoomLL: function(map, zoom, location) {
        // Never zoom out, or try to zoom farther than allowed.
        var zoomToApply = Math.max(
            map.getZoom(),
            Math.min(zoom, map.getMaxZoom()));

        map.setView(location, zoomToApply);
    }
};
