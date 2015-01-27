# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings

from calendar import timegm
from datetime import datetime

import json

from django.utils.timezone import make_aware, utc

from apps.event.models import EventRegistration
from apps.survey.models import (Blockface, Survey, Territory,
                                BlockfaceReservation)
from apps.users.models import TrustedMapper


def soft_launch(request):
    # Convert a truthy setting to a boolean
    if getattr(settings, 'SOFT_LAUNCH_ENABLED', True):
        soft_launch = True
    else:
        soft_launch = False
    return {'soft_launch': soft_launch}


def my_events_now(request):
    user = request.user
    if user.is_authenticated():
        events = EventRegistration.my_events_now(user)
        if len(events) > 0:
            return {'my_events_now': events}
    return {}


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

    return {
        'layers_json': json.dumps(_make_layers_context(request)),
        'nyc_bounds': {
            'xmin': float(settings.NYC_BOUNDS[0]),
            'ymin': float(settings.NYC_BOUNDS[1]),
            'xmax': float(settings.NYC_BOUNDS[2]),
            'ymax': float(settings.NYC_BOUNDS[3])
        }
    }


def _make_layers_context(request):
    tiler_url_format = \
        "%(tiler_url)s/%(cache_buster)s/%(db)s/%(type)s/{z}/{x}/{y}"

    if request.user.is_authenticated():
        params = '?user=%s' % request.user.pk
    else:
        params = ''

    context = {}
    for layer in ['progress', 'reservable', 'reservations']:
        tile_url = tiler_url_format % _make_tiler_url_kwargs(request, layer)
        context[layer] = {
            'tiles': tile_url + '.png' + params,
            'grids': tile_url + '.grid.json' + params,
        }

    return context


def _make_tiler_url_kwargs(request, layer):
    cache_busters = _tiler_cache_busters(request)
    return {'tiler_url': settings.TILER_URL,
            'cache_buster': cache_busters[layer],
            'db': settings.DATABASES['default']['NAME'],
            'type': layer}


def _tiler_cache_busters(request):
    blockface_updated_at = _get_last_updated_datetime(Blockface)
    survey_updated_at = _get_last_updated_datetime(Survey)
    territory_updated_at = _get_last_updated_datetime(Territory)
    reservation_updated_at = _get_last_updated_datetime(BlockfaceReservation)

    max_timestamp = lambda *datetimes: timegm(max(*datetimes).utctimetuple())

    reservations_cache_buster = max_timestamp(blockface_updated_at,
        reservation_updated_at)

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
        "progress": progress_cache_buster,
        "reservable": progress_cache_buster, # uses the same tables as progress
        "reservations": reservations_cache_buster
    }


def _get_last_updated_datetime(Model):
    try:
        return Model.objects.latest('updated_at').updated_at
    except Model.DoesNotExist:
        return make_aware(datetime.min, utc)
