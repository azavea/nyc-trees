# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.users.views.group import group_list_page


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


def training_list_page(request):
    # TODO: implement
    return {}


def retrieve_job_status(request):
    # TODO: implement
    pass


def groups_to_follow(request):
    ctx = group_list_page(request)
    ctx.update({'chunk_size': 2})
    return ctx
