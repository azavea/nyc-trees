# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.staticfiles.finders import get_finders
from django.contrib.flatpages.models import FlatPage

from apps.home.training import training_summary
from apps.home.training.types import FlatPageTrainingStep


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        training_flatpages = [step for step in training_summary.steps
                              if isinstance(step, FlatPageTrainingStep)]

        flatpages = {}

        # exit early if anything exists or file
        # is not found
        for step in training_flatpages:
            name = step.name
            src_path = 'flatpages/%s.html' % name
            for finder in get_finders():
                full_src_path = finder.find(src_path)
                if full_src_path:
                    flatpages[full_src_path] = step
                    break
            else:
                raise CommandError("static file '%s' should always exist. "
                                   "Did you delete one manually?" % src_path)

            url = '/%s/' % name
            if FlatPage.objects.filter(url=url).exists():
                raise CommandError("FlatPage '%s' already exists." % url)

        for full_src_path, step in flatpages.items():
            url = '/%s/' % step.name
            with open(full_src_path, 'r') as f:
                fp = FlatPage.objects.create(
                    title=step.description,
                    url=url,
                    template_name=step.flatpage_template_name,
                    content=f.read())
                fp.sites.add(settings.SITE_ID)
