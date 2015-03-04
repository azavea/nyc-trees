# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from calendar import timegm
from datetime import datetime

from django.conf import settings
from django.utils.timezone import make_aware, utc

from models import (Group, Blockface, Survey, Territory, BlockfaceReservation)
from apps.users.models import TrustedMapper


def get_context_for_progress_layer(request):
    models = [Blockface, Survey, Territory, BlockfaceReservation]
    if request.user.is_authenticated():
        models.append(TrustedMapper)
    return _get_context_for_layer("progress", models, request)


def get_context_for_reservable_layer(request):
    models = [Group, Blockface, Territory, BlockfaceReservation, TrustedMapper]
    return _get_context_for_layer("reservable", models, request)


def get_context_for_reservations_layer(request):
    models = [Blockface, BlockfaceReservation]
    return _get_context_for_layer("reservations", models, request)


def get_context_for_territory_layer(request, group_id):
    models = [Blockface, Territory]
    params = '?group=%s' % group_id
    return _get_context_for_layer("territory", models, request, params)


def get_context_for_territory_survey_layer(request, group_id):
    models = [Blockface, Territory, BlockfaceReservation]
    params = '?group=%s' % group_id
    return _get_context_for_layer("territory_survey", models, request, params)


def get_context_for_territory_admin_layer(request, group_id):
    models = [Blockface, Territory, BlockfaceReservation]
    params = '?group=%s' % group_id
    return _get_context_for_layer("territory_admin", models, request, params)


def _get_context_for_layer(layer_name, models, request, params=''):
    tiler_url_format = \
        "%(tiler_url)s/%(cache_buster)s/%(db)s/%(type)s/{z}/{x}/{y}"

    tile_url = tiler_url_format % {
        'tiler_url': settings.TILER_URL,
        'cache_buster': _get_cache_buster(models),
        'db': settings.DATABASES['default']['NAME'],
        'type': layer_name
    }

    if params == '' and request.user.is_authenticated():
        params = '?user=%s' % request.user.pk

    context = {
        'tile_url': tile_url + '.png' + params,
        'grid_url': tile_url + '.grid.json' + params,
    }

    return context


def _get_cache_buster(models):
    datetimes = [_get_last_updated_datetime(Model) for Model in models]

    max_timestamp = timegm(max(*datetimes).utctimetuple())
    return max_timestamp


def _get_last_updated_datetime(Model):
    try:
        return Model.objects.latest('updated_at').updated_at
    except Model.DoesNotExist:
        return make_aware(datetime.min, utc)
