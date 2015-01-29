# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.decorators import login_required

from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do

from apps.quiz import views as v


quiz_page = do(login_required,
               route(GET=do(render_template('quiz/quiz_page.html'),
                            v.quiz_page),
                     POST=do(render_template('quiz/quiz_complete_page.html'),
                             v.complete_quiz)))
