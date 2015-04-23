# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route, render_template

from apps.core.decorators import census_admin_do

from apps.census_admin import views as v


upload_group_polygons = census_admin_do(
    render_template('census_admin/upload_group_polygons.html'),
    route(GET=lambda x: {},
          POST=v.upload_group_polygons))
