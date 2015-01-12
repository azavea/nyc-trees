# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings as s

from calendar import timegm
from datetime import datetime

from django.utils.timezone import make_aware, utc

from apps.survey.models import Blockface, Survey


def settings(request):
    return {
        "tiler_url": s.TILER_URL,
        "db_name": s.DATABASES['default']['NAME'],
        'nyc_bounds': {
            'xmin': float(s.NYC_BOUNDS[0]),
            'ymin': float(s.NYC_BOUNDS[1]),
            'xmax': float(s.NYC_BOUNDS[2]),
            'ymax': float(s.NYC_BOUNDS[3])
        }
    }


def tiler_cache_busters(request):
    blockface_updated_at = _get_last_updated_datetime(Blockface)
    survey_updated_at = _get_last_updated_datetime(Survey)

    max_timestamp = lambda *datetimes: timegm(max(*datetimes).utctimetuple())

    return {
        "cache_buster": {
            "progress": max_timestamp(blockface_updated_at, survey_updated_at)
        }
    }


def _get_last_updated_datetime(Model):
    try:
        return Model.objects.latest('updated_at').updated_at
    except Model.DoesNotExist:
        return make_aware(datetime.min, utc)
