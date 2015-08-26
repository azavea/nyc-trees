# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import timedelta
from django.utils.timezone import now

from libs.sql import get_total_tree_count, get_surveyed_species, \
    get_block_count_past_week

from apps.core.models import User

from apps.event.models import Event, EventRegistration
from apps.event.event_list import all_events, EventList

from apps.home.training import training_summary

from apps.survey.models import Blockface, Survey

from apps.users import user_profile_context


def home_page(request):
    if request.user.is_authenticated():
        context = user_profile_context(request.user)
        context.update(training_summary.get_context(request.user))
        context['counts_all'] = _global_counts()
        context['counts_week'] = _global_counts(past_week=True)

        event_reg = EventRegistration.next_event_starting_soon(request.user)
        if event_reg:
            context['event'] = event_reg.event
            context['did_attend_event'] = event_reg.did_attend
    else:
        context = {
            'user': request.user,
            'counts_all': _global_counts()
        }

    all_events_list = (
        all_events
        .configure(chunk_size=10,
                   filterset_name=EventList.userFilters,
                   active_filter=EventList.Filters.ATTENDING)
        .as_context(request))

    context.update({'all_events': all_events_list})
    return context


def _global_counts(past_week=False):
    blocks_total = Blockface.objects.all().count()
    if past_week:
        blocks_mapped = get_block_count_past_week()
    else:
        blocks_mapped = Survey.objects.distinct('blockface').count()
    if blocks_mapped > 0:
        fraction_mapped = float(blocks_mapped) / float(blocks_total)
        blocks_percent = "{:.1%}".format(fraction_mapped)
    else:
        blocks_percent = "0.0%"
    if past_week:
        blocks_percent = '+' + blocks_percent

    user_count = User.objects.filter(is_active=True).count()
    attended_events = EventRegistration.objects.filter(did_attend=True) \
        .distinct('user_id').count()
    individual_mappers = User.objects.filter(is_active=True,
                                             individual_mapper=True).count()

    if past_week:
        week_ago = now() - timedelta(days=7)
        event_count = Event.objects \
            .filter(begins_at__lt=now(), ends_at__gte=week_ago) \
            .count()
    else:
        event_count = -999  # not needed

    # In order to show the tree count in a "ticker" we need to break it up
    # into digits and pad it with zeroes.
    tree_count = get_total_tree_count(past_week)
    trees_digits = [digit for digit in "{:07d}".format(tree_count)]

    surveyed_species = get_surveyed_species()
    # Distinct count, not total amount
    surveyed_species_count = len(surveyed_species)

    global_counts = {
        'species': surveyed_species_count,
        'species_by_name': surveyed_species,
        'tree': trees_digits,
        'block': blocks_mapped,
        'block_percent': blocks_percent,
        'user': user_count,
        'event': event_count,
        'attended_events': attended_events,
        'individual_mappers': individual_mappers
        }
    return global_counts


def individual_mapper_instructions(request):
    pass


def trusted_mapper_request_sent(request):
    pass


def about_faq_page(request):
    pass
