# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib import admin
import apps.users.models as m
admin.site.register(m.Follow)
admin.site.register(m.TrustedMapper)
admin.site.register(m.TrainingResult)
