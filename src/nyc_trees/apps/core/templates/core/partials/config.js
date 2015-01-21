{% load utils %}
(function(window, Object) {
    window.config = {
        "files": {
            "datetimepicker_polyfill.js": "{{ 'js/datetimepicker_polyfill.js'|static_url }}"
        },
        "urls": {
            "geocode": "{% url 'geocode' %}",
            "layers": {{ layers_json|safe }}
        },
        "bounds": [[{{nyc_bounds.ymin}}, {{nyc_bounds.xmin}}], [{{nyc_bounds.ymax}}, {{nyc_bounds.xmax}}]]
    };

    if (Object.freeze) {
        window.config = Object.freeze(window.config);
    }
}(window, Object));
