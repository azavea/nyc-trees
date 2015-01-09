{% load utils %}

window.config = {
    "files": {
        "datetimepicker_polyfill.js": "{{ 'js/datetimepicker_polyfill.js'|static_url }}"
    },
    "urls": {
        "geocode": "{% url 'geocode' %}",
        "layers": {
            "progress": {
                "tiles": "{{ tiler_url }}/{{ cache_buster.progress }}/{{ db_name }}/progress/{z}/{x}/{y}.png",
                "grids": "{{ tiler_url }}/{{ cache_buster.progress }}/{{ db_name }}/progress/{z}/{x}/{y}.grid.json"
            }
        }
    },
    "bounds": [[{{NYC_BOUNDS_YMIN}}, {{NYC_BOUNDS_XMIN}}], [{{NYC_BOUNDS_YMAX}}, {{NYC_BOUNDS_XMAX}}]]
};

if (Object.freeze) {
    window.config = Object.freeze(window.config);
}
