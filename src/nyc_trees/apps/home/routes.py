# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do

from apps.home import views as v
from apps.core.decorators import individual_mapper_do


home_page = route(GET=do(render_template('home/home.html'),
                         v.home_page))

about_faq_page = route(GET=do(render_template('home/about_faq.html'),
                              v.about_faq_page))

individual_mapper_instructions = individual_mapper_do(
    render_template('home/individual_mapper_instructions.html'),
    v.individual_mapper_instructions)

trusted_mapper_request_sent = individual_mapper_do(
    render_template('home/trusted_mapper_request_sent.html'),
    v.trusted_mapper_request_sent)
