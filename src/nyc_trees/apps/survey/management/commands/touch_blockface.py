# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from apps.survey.models import Blockface


class Command(BaseCommand):
    """
    Touch the Blockface table to refresh the map layer context.
    """

    def handle(self, *args, **options):
        b = Blockface.objects.first()
        b.updated_at = now()
        b.save()
