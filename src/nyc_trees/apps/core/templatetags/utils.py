# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import re

from django import template
from django.conf import settings


register = template.Library()
_remove_slash_re = re.compile(r'/+')


def _urljoin(*args):
    """Joins relative URLs, collapsing consecutive '/'"""
    url = "/".join(args)
    return _remove_slash_re.sub('/', url)


@register.filter
def static_url(static_file):
    if settings.DEBUG:
        return _urljoin(settings.STATIC_URL, static_file)

    static_file_mapping = settings.STATIC_FILES_MAPPING

    if static_file not in static_file_mapping:
        raise Exception('Static file %s not found in rev-manifest.json, '
                        'did you forget to run "npm run build"?' % static_file)

    return _urljoin(settings.STATIC_URL, static_file_mapping[static_file])
