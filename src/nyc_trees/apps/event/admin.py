# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
import apps.event.models as m


@admin.register(m.Event)
class EventAdmin(OSMGeoAdmin):
    openlayers_url = settings.ADMIN_OPENLAYERS_URL

admin.site.register(m.EventRegistration)
