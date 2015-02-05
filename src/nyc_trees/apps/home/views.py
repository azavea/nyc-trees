# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.home.training import training_summary


def home_page(request):
    training_steps = training_summary.get_context(request.user)
    return {'user': request.user, 'training_steps': training_steps}


def retrieve_job_status(request):
    # TODO: implement
    pass
