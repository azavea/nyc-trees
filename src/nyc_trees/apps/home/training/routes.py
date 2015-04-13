# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.decorators import login_required
from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do

from apps.users.views.group import group_list_page

from apps.core.decorators import user_must_have_online_training

from apps.home.training.decorators import render_flatpage

from apps.home.training import views as v

from apps.home.training.decorators import mark_user


groups_to_follow = route(
    GET=do(login_required,
           user_must_have_online_training,
           mark_user('training_finished_groups_to_follow'),
           render_template('home/groups_to_follow.html'),
           group_list_page))


training_list_page = route(GET=do(render_template('home/training.html'),
                                  v.training_list_page))

intro_quiz = do(login_required,
                route(GET=do(render_template('home/quiz_page.html'),
                             v.intro_quiz),
                      POST=do(render_template('home/quiz_complete_page.html'),
                              v.complete_quiz)))

training_instructions = route(GET=do(
    render_template('home/training_instructions.html'),
    v.training_instructions))


def make_flatpage_route(name):
    return route(GET=do(
        login_required,
        render_flatpage('/%s/' % name)))
