# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import urllib

from calendar import timegm
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware, utc

from apps.core.helpers import user_is_census_admin
from apps.survey.models import (Group, Blockface, Survey, BlockfaceReservation,
                                Borough, Territory, NeighborhoodTabulationArea)
from apps.users.models import TrustedMapper


def get_context_for_progress_layer():
    models = [Blockface, Survey]
    return _get_context_for_layer("progress", models)


def get_context_for_borough_progress_layer():
    models = [Blockface, Borough, Survey]
    return _get_context_for_layer("borough_progress", models)


def get_context_for_nta_progress_layer():
    models = [Blockface, NeighborhoodTabulationArea, Survey]
    return _get_context_for_layer("nta_progress", models)


@login_required
def get_context_for_user_progress_layer(request):
    models = [Blockface, Survey]
    return _get_context_for_layer("user_progress", models,
                                  {'user': request.user.pk})


def get_context_for_group_progress_layer():
    models = [Blockface, Survey, Territory]
    return _get_context_for_layer("group_progress", models)


def get_context_for_printable_event_map(group_id):
    models = [Blockface, Survey, Territory]
    return _get_context_for_layer("event_pdf", models,
                                  {'group': group_id})


@login_required
def get_context_for_reservable_layer(request):
    if user_is_census_admin(request.user):
        models = [Blockface, BlockfaceReservation]
        return _get_context_for_layer("admin_reservable", models,
                                      {'user': request.user.pk})
    else:
        models = [
            Group, Blockface, Territory, BlockfaceReservation, TrustedMapper]
        return _get_context_for_layer("user_reservable", models,
                                      {'user': request.user.pk})


@login_required
def get_context_for_reservations_layer(request):
    models = [Blockface, BlockfaceReservation]
    return _get_context_for_layer("user_reservations", models,
                                  {'user': request.user.pk})


@login_required
def get_context_for_printable_reservations_layer(request):
    models = [Blockface, BlockfaceReservation]
    return _get_context_for_layer("user_reservations_print", models,
                                  {'user': request.user.pk})


def get_context_for_territory_layer(group_id):
    models = [Blockface, Territory]
    return _get_context_for_layer("group_territory", models,
                                  {'group': group_id})


def get_context_for_territory_survey_layer(group_id):
    models = [Blockface, Territory, BlockfaceReservation]
    return _get_context_for_layer("group_territory_survey", models,
                                  {'group': group_id})


def get_context_for_territory_admin_layer(group_id):
    models = [Blockface, Territory, BlockfaceReservation]
    return _get_context_for_layer("group_territory_admin", models,
                                  {'group': group_id})


def get_group_territory_modification_time(request):
    return _get_max_modification_time([Group])


def _get_context_for_layer(layer_name, models, params=None):
    tiler_url_format = \
        "%(tiler_url)s/%(cache_buster)s/%(db)s/%(type)s/{z}/{x}/{y}"

    tile_url = tiler_url_format % {
        'tiler_url': settings.TILER_URL,
        'cache_buster': _get_cache_buster(models, params),
        'db': settings.DATABASES['default']['NAME'],
        'type': layer_name
    }

    if params:
        query = '?' + urllib.urlencode(params)
    else:
        query = ''

    context = {
        'tile_url': tile_url + '.png' + query,
        'grid_url': tile_url + '.grid.json' + query,
    }

    return context


def _get_cache_buster(models, params=None):
    max_datetime = _get_max_modification_time(models, params)

    max_timestamp = timegm(max_datetime.utctimetuple())
    return max_timestamp


def _get_max_modification_time(models, params=None):
    datetimes = [_get_last_updated_datetime(Model, params) for Model in models]

    return max(datetimes)


def _get_last_updated_datetime(Model, params):
    try:
        # Unlike the other models we use for cache busters, Territory rows are
        # deleted.  To work around this, we check Group.territory_updated_at
        if Model == Territory:
            if params and 'group' in params:
                group = Group.objects.get(pk=params['group'])
            else:
                group = Group.objects.latest('territory_updated_at')

            if group.territory_updated_at is not None:
                return group.territory_updated_at
            else:
                return make_aware(datetime.min, utc)
        else:
            return Model.objects.latest('updated_at').updated_at
    except (Model.DoesNotExist, Group.DoesNotExist):
        return make_aware(datetime.min, utc)
