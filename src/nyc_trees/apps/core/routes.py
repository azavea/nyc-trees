# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route

from apps.core.views import js_settings


js_settings = route(GET=js_settings)
