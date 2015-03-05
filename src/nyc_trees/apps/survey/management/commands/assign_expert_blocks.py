# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import Group
from apps.survey.models import Blockface, Territory


class Command(BaseCommand):
    """
    Assign all expert_required blockfaces to a specified group

    Usage:

    ./manage.py assign_expert_blocks some-group-slug
    """
    @transaction.atomic
    def handle(self, *args, **options):
        group_slug = args[0]
        group = Group.objects.get(slug=group_slug)
        print("Assigning expert blocks to %s" % group.name)

        already_assigned_ids = Territory.objects.filter(group=group)\
                                                .values_list('blockface_id',
                                                             flat=True)
        print("Skipping %d blocks already assigned" %
              already_assigned_ids.count())

        new_expert_blocks = Blockface.objects\
                                     .filter(expert_required=True)\
                                     .exclude(id__in=already_assigned_ids)

        assigned_to_others = Territory.objects\
                                      .filter(blockface__in=new_expert_blocks)
        print("Removing %d assignments to groups other than %s" %
              (assigned_to_others.count(), group.name))
        assigned_to_others.delete()

        print("Assigning %d blocks to %s" %
              (new_expert_blocks.count(), group.name))
        for blockface in new_expert_blocks:
            Territory.objects.create(group=group, blockface=blockface)
