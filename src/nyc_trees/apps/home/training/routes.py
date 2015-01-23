# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do

from apps.home.training import views as v

groups_to_follow = route(GET=do(render_template('home/groups_to_follow.html'),
                                v.groups_to_follow))

training_list_page = route(GET=do(render_template('home/training.html'),
                                  v.training_list_page))
