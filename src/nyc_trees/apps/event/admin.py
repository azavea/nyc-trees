# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
import apps.event.models as m


admin.site.register(m.Event, OSMGeoAdmin)
admin.site.register(m.EventRegistration)
