# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.shortcuts import get_object_or_404

from django_tinsel.decorators import render_template

from apps.core.models import Group


def group_list_page(request):
    # TODO: implement
    pass


def group_detail(request, group_slug):
    group = get_object_or_404(Group, slug=group_slug)
    return _render_group_detail(request, group)


@render_template('groups/detail.html')
def _render_group_detail(request, group):
    context = {
        'group': group
    }
    return context


def edit_group(request, group_slug):
    # TODO: implement
    pass


def follow_group(request, group_slug):
    # TODO: implement
    pass


def unfollow_group(request, group_slug):
    # TODO: implement
    pass


def start_group_map_print_job(request, group_slug):
    # TODO: implement
    pass


def group_mapping_priveleges_page(request, group_slug):
    # TODO: implement
    pass


def give_user_mapping_priveleges(request, group_slug, username):
    # TODO: implement
    pass


def remove_user_mapping_priveleges(request, group_slug, username):
    # TODO: implement
    pass
