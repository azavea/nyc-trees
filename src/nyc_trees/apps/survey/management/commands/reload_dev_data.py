# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.survey.models import (Tree, Survey, Blockface, Territory,
                                BlockfaceReservation)


class Command(BaseCommand):
    """
    Create a new instance with a single editing role.
    """

    option_list = BaseCommand.option_list

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Deleting all existing survey and blockface data')

        Tree.objects.all().delete()
        Survey.objects.all().delete()
        Territory.objects.all().delete()
        BlockfaceReservation.objects.all().delete()
        Blockface.objects.all().delete()

        self.stdout.write('Importing blockface fixture')

        for i in range(1, 8):
            call_command(
                'loaddata',
                '/opt/app/apps/survey/fixtures/blockface_%d.json' % i)
