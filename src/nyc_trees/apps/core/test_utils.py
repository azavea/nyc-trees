# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from cStringIO import StringIO

from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.geos import Point
from django.test import RequestFactory
from django.utils.timezone import now

from apps.event.models import Event


def make_request(params={}, user=None, method='GET', body=None, file=None,
                 group=None, **extra):
    if user is None:
        user = AnonymousUser()

    if not extra:
        extra = {}
    if body:
        body_stream = StringIO(body)
        extra['wsgi.input'] = body_stream
        extra['CONTENT_LENGTH'] = len(body)

    if file:
        post_data = {'file': file}
        req = RequestFactory().post("hello/world", post_data, **extra)
    elif method == 'POST':
        req = RequestFactory().post("hello/world", params, **extra)
    else:
        req = RequestFactory().get("hello/world", params, **extra)
        req.method = method

    setattr(req, 'user', user)
    setattr(req, 'group', group)

    return req


def make_event(group, **kwargs):
    defaults = {
        'group': group,
        'title': "The event",
        'contact_email': "a@b.com",
        'address': "123 Main St",
        'location': Point(0, 0),
        'max_attendees': 100,
        'begins_at': now(),
        'ends_at': now()
    }
    defaults.update(kwargs)

    e = Event(**defaults)
    e.clean_and_save()

    return e
