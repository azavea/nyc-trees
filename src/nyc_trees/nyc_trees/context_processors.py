# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.core.urlresolvers import reverse

from apps.users.views.user import USER_SETTINGS_PRIVACY_TAB_ID


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
