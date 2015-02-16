# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.core.urlresolvers import reverse

from apps.event.models import EventRegistration
from apps.users.views.user import USER_SETTINGS_PRIVACY_TAB_ID


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


def user_settings_privacy_url(request):
    base_url = reverse('user_profile_settings')
    full_url = '%s#%s' % (base_url, USER_SETTINGS_PRIVACY_TAB_ID)
    return {'user_settings_privacy_url': full_url}


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
        'nyc_bounds': {
            'xmin': float(settings.NYC_BOUNDS[0]),
            'ymin': float(settings.NYC_BOUNDS[1]),
            'xmax': float(settings.NYC_BOUNDS[2]),
            'ymax': float(settings.NYC_BOUNDS[3])
        }
    }
