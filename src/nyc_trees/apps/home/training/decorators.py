# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from functools import wraps

from django.db import transaction

from django.http import Http404

from django.contrib.flatpages.views import flatpage


def render_flatpage(url):
    def fn(request, *args, **kwargs):
        return flatpage(request, url)
    return fn


def mark_user(attr, extra_block=None):
    def outer_decorator(view_fn):
        @wraps(view_fn)
        @transaction.atomic
        def wrapper(request, *args, **kwargs):
            user = request.user

            if user.is_authenticated() and not getattr(user, attr):
                setattr(user, attr, True)
                user.save()
                should_trigger_extra_block = True
            else:
                should_trigger_extra_block = False

            ctx = view_fn(request, *args, **kwargs)

            # in case the extra block does things that don't
            # work well with database transactions (like email)
            # postpone it to the end of the transaction block
            # to avoid cases in which an email is sent but the
            # transaction is rolled back due to a later exception
            if extra_block and should_trigger_extra_block:
                extra_block(user)

            return ctx
        return wrapper
    return outer_decorator


def require_visitability(step):
    def outer_decorator(view_fn):
        @wraps(view_fn)
        @transaction.atomic
        def wrapper(request, *args, **kwargs):
            if not step.is_visitable(request.user):
                raise Http404()
            else:
                return view_fn(request, *args, **kwargs)
        return wrapper
    return outer_decorator
