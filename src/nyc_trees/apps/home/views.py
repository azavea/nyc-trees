# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.core.views import map_legend
from apps.home.training import training_summary
from apps.survey.layer_context import get_context_for_progress_layer
from apps.users import user_profile_context


def home_page(request):
    if request.user.is_authenticated():
        context = user_profile_context(request.user, True)
        context['training_steps'] = training_summary.get_context(request.user)
        return context
    else:
        return {'user': request.user}


def progress_page(request):
    context = map_legend(request)
    context['layer'] = get_context_for_progress_layer(request)
    return context


def retrieve_job_status(request):
    # TODO: implement
    pass


def individual_mapper_instructions(request):
    pass
