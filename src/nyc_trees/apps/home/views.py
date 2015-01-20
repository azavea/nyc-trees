# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from functools import wraps

from django.contrib.flatpages.views import flatpage
from apps.users.views.group import group_list_page


def home_page(request):
    # TODO: implement
    return {}


def training_list_page(request):
    # TODO: implement
    return {}


def retrieve_job_status(request):
    # TODO: implement
    pass


def redirect_to_flat_page(url):
    def fn(request, *args, **kwargs):
        return flatpage(request, url)
    return fn


def mark_user_on_success(attr):
    def outer_decorator(view_fn):
        @wraps(view_fn)
        def wrapper(request, *args, **kwargs):
            # do this first to make sure the wrapped view doesn't
            # raise
            ctx = view_fn(request, *args, **kwargs)
            user = request.user
            if user.is_authenticated() and not getattr(user, attr):
                setattr(user, attr, True)
                user.save()
            return ctx
        return wrapper
    return outer_decorator


def groups_to_follow(request):
    ctx = group_list_page(request)
    ctx.update({'chunk_size': 2})
    return ctx
