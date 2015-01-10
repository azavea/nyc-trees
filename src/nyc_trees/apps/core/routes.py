# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route

from apps.core.views import settings_js


settings_js = route(GET=settings_js)
