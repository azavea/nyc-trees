# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import datetime
from calendar import timegm

from django.conf import settings
from django.shortcuts import render_to_response
from django.utils.timezone import make_aware, utc

from apps.survey.models import Blockface, Survey


def js_settings(request):
    blockface_updated_at = _get_last_updated_datetime(Blockface)
    survey_updated_at = _get_last_updated_datetime(Survey)

    max_timestamp = lambda *datetimes: timegm(max(*datetimes).utctimetuple())

    return render_to_response('core/settings.js', {
        "tiler_url": settings.TILER_URL,
        "db_name": settings.DATABASES['default']['NAME'],
        "cache_buster": {
            "progress": max_timestamp(blockface_updated_at, survey_updated_at)
        }
    })


def _get_last_updated_datetime(Model):
    try:
        return Model.objects.latest('updated_at').updated_at
    except Model.DoesNotExist:
        return make_aware(datetime.min, utc)
