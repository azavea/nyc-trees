# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.http import Http404
from functools import wraps


def route(**kwargs):
    """
    Route a request to different views based on http verb.

    Kwargs should be 'GET', 'POST', 'PUT', 'DELETE' or 'ELSE',
    where the first four map to a view to route to for that type of
    request method/verb, and 'ELSE' maps to a view to pass the request
    to if the given request method/verb was not specified.
    """
    def routed(request, *args2, **kwargs2):
        method = request.method
        if method in kwargs:
            req_method = kwargs[method]
            return req_method(request, *args2, **kwargs2)
        elif 'ELSE' in kwargs:
            return kwargs['ELSE'](request, *args2, **kwargs2)
        else:
            raise Http404()
    return routed


def is_logged_in(view_fn):
    # TODO: implement
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        return view_fn(request, *args, **kwargs)
    return wrapper


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
