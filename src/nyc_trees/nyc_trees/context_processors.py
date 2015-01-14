# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings

from calendar import timegm
from datetime import datetime

from django.utils.timezone import make_aware, utc

from apps.survey.models import (Blockface, Survey, Territory,
                                BlockfaceReservation)
from apps.users.models import TrustedMapper


def config(request):
    # At the time this function was written, the generated context was
    # only used in the base.html template, and our AJAX requests all
    # render partials, not full templates inheriting from base. Given
    # those constraints, we can skip generating this context, which
    # saves some database query time.
    if request.is_ajax():
        # The Django 1.7 docs say "Each context processor _must_ return
        # a dictionary."
        return {}

    cache_busters = _tiler_cache_busters(request)

    tile_url_format = \
        "%(tiler_url)s/%(cache_buster)s/%(db)s/%(type)s/{z}/{x}/{y}.png"
    grid_url_format = \
        "%(tiler_url)s/%(cache_buster)s/%(db)s/%(type)s/{z}/{x}/{y}.grid.json"

    progress_kwargs = {'tiler_url': settings.TILER_URL,
                       'cache_buster': cache_busters['progress'],
                       'db': settings.DATABASES['default']['NAME'],
                       'type': 'progress'}

    progress_tiles = tile_url_format % progress_kwargs
    progress_grids = grid_url_format % progress_kwargs

    if request.user.is_authenticated():
        extra_params = "?user=%s" % request.user.pk
        progress_tiles += extra_params
        progress_grids += extra_params

    return {
        "progress_tiles_url": progress_tiles,
        "progress_grids_url": progress_grids,
        'nyc_bounds': {
            'xmin': float(settings.NYC_BOUNDS[0]),
            'ymin': float(settings.NYC_BOUNDS[1]),
            'xmax': float(settings.NYC_BOUNDS[2]),
            'ymax': float(settings.NYC_BOUNDS[3])
        }
    }


def _tiler_cache_busters(request):
    blockface_updated_at = _get_last_updated_datetime(Blockface)
    survey_updated_at = _get_last_updated_datetime(Survey)
    territory_updated_at = _get_last_updated_datetime(Territory)
    reservation_updated_at = _get_last_updated_datetime(BlockfaceReservation)

    max_timestamp = lambda *datetimes: timegm(max(*datetimes).utctimetuple())

    if request.user.is_authenticated():
        mapper_updated_at = _get_last_updated_datetime(TrustedMapper)

        progress_cache_buster = max_timestamp(
            blockface_updated_at, survey_updated_at, territory_updated_at,
            reservation_updated_at, mapper_updated_at)
    else:
        progress_cache_buster = max_timestamp(
            blockface_updated_at, survey_updated_at, territory_updated_at,
            reservation_updated_at)

    return {
        "progress": progress_cache_buster
    }


def _get_last_updated_datetime(Model):
    try:
        return Model.objects.latest('updated_at').updated_at
    except Model.DoesNotExist:
        return make_aware(datetime.min, utc)
