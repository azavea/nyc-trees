# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.decorators import login_required
from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do
from apps.home.training.decorators import render_flatpage

from apps.home.training import views as v


groups_to_follow = route(GET=do(login_required,
                                render_template('home/groups_to_follow.html'),
                                v.groups_to_follow))

training_list_page = route(GET=do(render_template('home/training.html'),
                                  v.training_list_page))

intro_quiz = do(login_required,
                route(GET=do(render_template('home/quiz_page.html'),
                             v.intro_quiz),
                      POST=do(render_template('home/quiz_complete_page.html'),
                              v.complete_quiz)))


def make_flatpage_route(name):
    return route(GET=do(
        login_required,
        render_flatpage('/%s/' % name)))
