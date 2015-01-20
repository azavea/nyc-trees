# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.staticfiles.finders import get_finders
from django.contrib.flatpages.models import FlatPage


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        flat_pages = {}

        # exit early if anything exists or file
        # is not found
        for name in settings.TRAINING_FLAT_PAGES:
            src_path = 'flatpages/%s.html' % name
            for finder in get_finders():
                full_src_path = finder.find(src_path)
                if full_src_path:
                    flat_pages[name] = full_src_path
                    break
            else:
                raise CommandError("static file '%s' should always exist. "
                                   "Did you delete one manually?" % src_path)

            url = '/%s/' % name
            if FlatPage.objects.filter(url=url).exists():
                raise CommandError("FlatPage '%s' already exists." % url)

        for name, path in flat_pages.items():
            with open(full_src_path, 'r') as f:
                fp = FlatPage.objects.create(url=url,
                                             content=f.read())
                fp.sites.add(settings.SITE_ID)
