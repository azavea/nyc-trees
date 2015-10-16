# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import re
import waffle

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect


class FullAccessMiddleware(object):
    def __init__(self):
        self.redirect_url = settings.LIMITED_ACCESS_REDIRECT_URL
        regexes = settings.LIMITED_ACCESS_REGEXES
        self.regexes = [re.compile(r) for r in regexes]

    def process_view(self, request, view_func, view_args, view_kwargs):
        if waffle.flag_is_active(request, 'full_access'):
            return None

        allowed = ((request.path == self.redirect_url) or
                   any(r.match(request.path) for r in self.regexes))

        if not allowed:
            return redirect(self.redirect_url)


# Author: Tony Abou-Assaleh
# Source: http://stackoverflow.com/a/7871831
class BannedUserMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        if request.user.is_banned:
            logout(request)
