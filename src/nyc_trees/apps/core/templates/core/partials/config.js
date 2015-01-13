{% load utils %}
(function(window, Object) {
    window.config = {
        "files": {
            "datetimepicker_polyfill.js": "{{ 'js/datetimepicker_polyfill.js'|static_url }}"
        },
        "urls": {
            "geocode": "{% url 'geocode' %}",
            "layers": {
                "progress": {
                    "tiles": "{{ progress_tiles_url }}",
                    "grids": "{{ progress_grids_url }}"
                }
            }
        },
        "bounds": [[{{nyc_bounds.ymin}}, {{nyc_bounds.xmin}}], [{{nyc_bounds.ymax}}, {{nyc_bounds.xmax}}]]
    };

    if (Object.freeze) {
        window.config = Object.freeze(window.config);
    }
}(window, Object));
