# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from functools import wraps


def is_census_admin(view_fn):
    # TODO: implement
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        return view_fn(request, *args, **kwargs)
    return wrapper


def is_group_admin(view_fn):
    # TODO: implement
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        return view_fn(request, *args, **kwargs)
    return wrapper


def has_training(view_fn):
    # TODO: implement
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        return view_fn(request, *args, **kwargs)
    return wrapper


def is_individual_mapper(view_fn):
    # TODO: implement
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        return view_fn(request, *args, **kwargs)
    return wrapper
