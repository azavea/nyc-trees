# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from cStringIO import StringIO

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory


def make_request(params={}, user=None, method='GET', body=None, file=None):
    if user is None:
        user = AnonymousUser()

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

    return req
