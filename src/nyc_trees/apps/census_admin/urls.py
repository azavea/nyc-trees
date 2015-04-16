# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route

from apps.core.decorators import census_admin_do
from apps.census_admin.views import (start_admin_users_job,
                                     start_admin_surveys_job, admin_edits_page,
                                     admin_edits_partial,
                                     admin_training_material_list,
                                     admin_training_material)


# These URLs have the prefix 'census_admin/'
urlpatterns = patterns(
    '',
)
