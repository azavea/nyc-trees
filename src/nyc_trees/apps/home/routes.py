# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do

from apps.home import views as v


home_page = route(GET=do(render_template('home/home.html'),
                         v.home_page))

progress_page = route(GET=do(render_template('home/progress.html'),
                             v.progress_page))

retrieve_job_status = do(v.retrieve_job_status)
