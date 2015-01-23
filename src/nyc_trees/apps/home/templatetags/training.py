# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django import template

from apps.home.training import training_summary

register = template.Library()


@register.filter
def flatpage_next_url(flatpage):
    # the url for this flatpage must have a TrainingStep
    # that matches the url without slashes
    # ex: `/the_flatpage/` must correspond to a TrainingStep
    # called `the_flatpage`
    flatpage_name = flatpage.url[1:-1]
    return training_summary.get_step(flatpage_name).mark_progress_url()
