# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from functools import wraps

from django.db import transaction

from django.contrib.flatpages.views import flatpage


def render_flatpage(url):
    def fn(request, *args, **kwargs):
        return flatpage(request, url)
    return fn


def mark_user(attr):
    def outer_decorator(view_fn):
        @wraps(view_fn)
        @transaction.atomic
        def wrapper(request, *args, **kwargs):
            user = request.user

            if user.is_authenticated() and not getattr(user, attr):
                setattr(user, attr, True)
                user.save()

            ctx = view_fn(request, *args, **kwargs)
            return ctx
        return wrapper
    return outer_decorator
