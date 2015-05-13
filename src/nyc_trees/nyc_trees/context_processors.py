# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.core.urlresolvers import reverse

from apps.users.views.user import USER_SETTINGS_PRIVACY_TAB_ID
from apps.event.models import EventRegistration


def treecorder_urls(request):
    user = request.user
    # At the time this function was written, the generated context was
    # only used in the base.html template, and our AJAX requests all
    # render partials, not full templates inheriting from base. Given
    # those constraints, we can skip generating this context, which
    # saves some database query time.
    if request.is_ajax():
        return {}

    if not request.user.is_authenticated():
        return {
            # The key of the URLs dict is not used when there is only one entry
            'treecorder_urls': {
                '': reverse('auth_login') + '?next=' + request.get_full_path()
            }
        }

    urls = {}

    attended_events, unattended_events = EventRegistration.my_events_now(user)

    for event in unattended_events:
        label = 'Check into event %s for %s' % (event.title, event.group.name)
        urls[label] = reverse('event_user_check_in_page', kwargs={
            'group_slug': event.group.slug, 'event_slug': event.slug})

    for event in attended_events:
        label = 'Map at event %s for %s' % (event.title, event.group.name)
        urls[label] = reverse('survey_from_event', kwargs={
            'group_slug': event.group.slug, 'event_slug': event.slug})

    if user.individual_mapper:
        if user.blockfacereservation_set.current().exists():
            urls['Map your reserved block edges'] = reverse('survey')

    # If there are no events and no reserved blocks, we should link to a either
    # the reservations page or the apprpriate instructions page
    if not urls:
        # The key of the URLs dict is not used when there is only one entry
        if user.individual_mapper:
            urls[''] = reverse('reservations')
        elif not user.training_complete:
            urls[''] = reverse('training_instructions')
        else:
            urls[''] = reverse('reservations_instructions')

    return {
        'treecorder_urls': urls
    }


def user_settings_privacy_url(request):
    base_url = reverse('user_profile_settings')
    full_url = '%s#%s' % (base_url, USER_SETTINGS_PRIVACY_TAB_ID)
    return {'user_settings_privacy_url': full_url}


def config(request):
    return {
        'nyc_bounds': {
            'xmin': float(settings.NYC_BOUNDS[0]),
            'ymin': float(settings.NYC_BOUNDS[1]),
            'xmax': float(settings.NYC_BOUNDS[2]),
            'ymax': float(settings.NYC_BOUNDS[3])
        }
    }
