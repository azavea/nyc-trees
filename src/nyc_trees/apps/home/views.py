# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import render_template


@render_template('home/home.html')
def home_page(request):
    # TODO: implement
    return {}


@render_template('home/progress.html')
def progress_page(request):
    # TODO: implement
    return {}


def retrieve_job_status(request):
    # TODO: implement
    pass
