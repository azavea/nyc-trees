# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib import admin

import apps.core.models as m
admin.site.register(m.User)
admin.site.register(m.Group)
