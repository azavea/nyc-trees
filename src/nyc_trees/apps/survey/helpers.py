# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.survey.models import Survey, Territory


def group_percent_completed(group):
    group_blocks = Territory.objects \
        .filter(group=group) \
        .values_list('blockface_id', flat=True)

    group_blocks_count = group_blocks.count()

    if group_blocks_count > 0:
        completed_blocks = Survey.objects \
            .complete() \
            .filter(blockface_id__in=group_blocks) \
            .filter(blockface__is_available=False) \
            .distinct('blockface')

        return "{:.1%}".format(
            float(completed_blocks.count()) / float(group_blocks.count()))
    else:
        return "0.0%"
