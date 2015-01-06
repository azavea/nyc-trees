# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


def home_page(request):
    # TODO: implement
    return {}


def progress_page(request):
    context = {
        'legend_entries': [
            {'css_class': 'mapped-by-you', 'label': 'Mapped by you'},
            {'css_class': 'mapped-by-others', 'label': 'Mapped by others'},
            {'css_class': 'not-mapped', 'label': 'Not mapped'},
        ]
    }
    return context


def retrieve_job_status(request):
    # TODO: implement
    pass
