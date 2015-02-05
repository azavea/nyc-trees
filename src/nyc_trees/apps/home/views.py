# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.home.training import training_summary
from apps.users import user_profile_context


def home_page(request):
    if request.user.is_authenticated():
        context = user_profile_context(request.user, True)
        context['training_steps'] = training_summary.get_context(request.user)
        return context
    else:
        return {'user': request.user}


def retrieve_job_status(request):
    # TODO: implement
    pass
