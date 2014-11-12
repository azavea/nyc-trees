# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib import admin
import apps.event.models as m
admin.site.register(m.Event)
admin.site.register(m.EventRegistration)
