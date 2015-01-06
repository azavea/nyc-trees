# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route, json_api_call
from django_tinsel.utils import decorate as do

from apps.geocode import views as v

geocode = route(GET=do(json_api_call,
                       v.geocode))
