# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from functools import wraps, partial

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from django_tinsel.utils import decorate as do

from apps.core.helpers import (user_is_census_admin, user_is_group_admin,
                               user_is_individual_mapper,
                               user_has_online_training,
                               user_has_field_training)
from apps.core.models import Group


def group_request(view_fn):
    """
    This decorator consumes the `group_slug` argument of the view
    function being wrapped, fetches the Group the `group_slug`
    identifies and sets it on `request.group`.  Any chained view
    functions downstream from this decorator must not expect a
    `group_slug` argument. They can access `request.group` directly.
    """
    @wraps(view_fn)
    def wrapper(request, group_slug, *args, **kwargs):
        request.group = get_object_or_404(Group, slug=group_slug)
        return view_fn(request, *args, **kwargs)
    return wrapper


def user_must_be_census_admin(view_fn):
    """
    Raise PermissionDenied if `request.user` is not a census admin
    """
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        if user_is_census_admin(request.user):
            return view_fn(request, *args, **kwargs)
        else:
            raise PermissionDenied('%s is not a census administrator'
                                   % request.user)
    return wrapper


def user_must_be_group_admin(view_fn):
    """
    Raise PermissionDenied if `request.user` is not allowed to
    administer `request.group`.
    """
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        if user_is_group_admin(request.user, request.group):
            return view_fn(request, *args, **kwargs)
        else:
            raise PermissionDenied('%s is not an administrator of %s'
                                   % (request.user, request.group))
    return wrapper


def user_must_have_online_training(view_fn):
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        if user_has_online_training(request.user):
            return view_fn(request, *args, **kwargs)
        else:
            raise PermissionDenied('%s has not completed online training yet'
                                   % request.user)
    return wrapper


def user_must_have_field_training(view_fn):
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        if user_has_field_training(request.user):
            return view_fn(request, *args, **kwargs)
        else:
            raise PermissionDenied('%s has not attended a training event yet'
                                   % request.user)
    return wrapper


def user_must_be_individual_mapper(view_fn):
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        if user_is_individual_mapper(request.user):
            return view_fn(request, *args, **kwargs)
        else:
            raise PermissionDenied('%s is not an individual mapper'
                                   % request.user)
    return wrapper


def update_with(callable_or_dict):
    def outer(view_fn):
        @wraps(view_fn)
        def inner(request, *args, **kwargs):
            ctx = view_fn(request, *args, **kwargs)
            if not isinstance(ctx, dict):
                # if it's already been lifted from a context
                # to an http object, it's usually because an
                # error or redirect happened before instead
                # in that case, just pass it through
                pass
            elif callable(callable_or_dict):
                ctx.update(callable_or_dict(request, *args, **kwargs))
            else:
                ctx.update(callable_or_dict)
            return ctx
        return inner
    return outer

##############################################################################
# Composite Route Helpers

group_admin_do = partial(do,
                         login_required,
                         group_request,
                         user_must_be_group_admin)

census_admin_do = partial(do,
                          login_required,
                          user_must_be_census_admin)

individual_mapper_do = partial(do,
                               login_required,
                               user_must_be_individual_mapper)
