{% load utils %}
(function(window, Object) {
    window.config = {
        "files": {
            "dtpPolyfill": "{{ 'js/datetimepicker_polyfill.js'|static_url }}"
        },
        "urls": {
            "geocode": "{% url 'geocode' %}",
            "geojson": {
                "events": "{% url 'future_events_geojson' %}"
            }
        },
        "bounds": [[{{nyc_bounds.ymin}}, {{nyc_bounds.xmin}}], [{{nyc_bounds.ymax}}, {{nyc_bounds.xmax}}]]
    };

    if (Object.freeze) {
        window.config = Object.freeze(window.config);
    }
}(window, Object));
