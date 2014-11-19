# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from functools import wraps

from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext


def decorate(*reversed_views):
    """
    provide a syntax decorating views without nested calls.

    instead of:
    instance_request(json_api_call(etag(<hash_fn>)(<view_fn>)))

    you can write:
    decorate(instance_request, json_api_call, etag(<hash_fn>), <view_fn>)
    """
    fns = reversed_views[::-1]
    view = fns[0]
    for wrapper in fns[1:]:
        view = wrapper(view)
    return view


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


def render_template(template):
    """
    takes a template to render to and returns a function that
    takes an object to render the data for this template.

    If callable_or_dict is callable, it will be called with
    the request and any additional arguments to produce the
    template paramaters. This is useful for a view-like function
    that returns a dict-like object instead of an HttpResponse.

    Otherwise, callable_or_dict is used as the parameters for
    the rendered response.
    """
    def outer_wrapper(callable_or_dict=None, statuscode=None, **kwargs):
        def wrapper(request, *args, **wrapper_kwargs):
            if callable(callable_or_dict):
                params = callable_or_dict(request, *args, **wrapper_kwargs)
            else:
                params = callable_or_dict

            # If we want to return some other response
            # type we can, that simply overrides the default
            # behavior
            if params is None or isinstance(params, dict):
                resp = render_to_response(template, params,
                                          RequestContext(request), **kwargs)
            else:
                resp = params

            if statuscode:
                resp.status_code = statuscode

            return resp

        return wrapper
    return outer_wrapper


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
