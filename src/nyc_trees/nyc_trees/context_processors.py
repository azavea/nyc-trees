# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings


def nyc_bounds(request):
    return {'NYC_BOUNDS_XMIN': float(settings.NYC_BOUNDS[0]),
            'NYC_BOUNDS_YMIN': float(settings.NYC_BOUNDS[1]),
            'NYC_BOUNDS_XMAX': float(settings.NYC_BOUNDS[2]),
            'NYC_BOUNDS_YMAX': float(settings.NYC_BOUNDS[3])}
